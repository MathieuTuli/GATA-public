import os
import json
import tempfile
import numpy as np
from os.path import join as pjoin

from agent import Agent
import evaluate
import generic
import reinforcement_learning_dataset


def run_eval():

    config = generic.load_config()
    agent = Agent(config)
    output_dir = "."
    data_dir = "."

    # make game environments
    requested_infos = agent.select_additional_infos()
    games_dir = "./"

    eval_env, num_eval_game = reinforcement_learning_dataset.get_evaluation_game_env(games_dir + config['rl']['data_path'],
                                                                                     config['rl']['difficulty_level'],
                                                                                     requested_infos,
                                                                                     agent.eval_max_nb_steps_per_episode,
                                                                                     agent.eval_batch_size,
                                                                                     valid_or_test="test")

    json_file_name = agent.experiment_tag.replace(" ", "_")
    # load pretrained models
    agent.load_pretrained_model(
        agent.load_from_tag + ".pt", load_partial_graph=False)

    # evaluate
    if agent.real_valued_graph:
        agent.load_pretrained_graph_generation_model(
            data_dir + "/" + agent.load_graph_generation_model_from_tag + ".pt")
        eval_game_points, eval_game_points_normalized, eval_game_step, detailed_scores, success = evaluate.evaluate_rl_with_real_graphs(
            eval_env, agent, num_eval_game)
        command_generation_f1 = 0.0
    else:
        if agent.eval_g_belief:
            agent.load_pretrained_graph_generation_model(
                data_dir + "/" + agent.load_graph_generation_model_from_tag + ".pt")
            eval_game_points, eval_game_points_normalized, eval_game_step, command_generation_f1, detailed_scores = evaluate.evaluate_belief_mode(
                eval_env, agent, num_eval_game)
        else:
            eval_game_points, eval_game_points_normalized, eval_game_step, _, detailed_scores = evaluate.evaluate(
                eval_env, agent, num_eval_game)
            command_generation_f1 = 0.0

    # write accuracies down into file
    _s = json.dumps({"eval game points": str(eval_game_points),
                     "eval normalized game points": str(eval_game_points_normalized),
                     "eval steps": str(eval_game_step),
                     "test_success": str(success),
                     "command generation f1": str(command_generation_f1),
                     "detailed scores": detailed_scores})
    diff = config['rl']['difficulty_level']
    seed = config['general']['random_seed']
    with open(output_dir + "/" + json_file_name + f'test_{diff}_{seed}.json', 'a+') as outfile:
        outfile.write(_s + '\n')
        outfile.flush()


if __name__ == '__main__':
    run_eval()
