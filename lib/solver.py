#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" board solver module

Usable as a library but also as a stand-alone process for pypy integration
"""


def in_board(pos):
  x, y = pos
  return (0 <= x < 6) and (0 <= y < 5)


def recurse_paths(cursor, path=tuple(), depth=2, board=None):
  newpath = path + (cursor,)

  total_paths = [newpath]
  if len(path) >= depth:
    return total_paths

  x, y = cursor
  dirs = (
    (x - 1, y),
    (x + 1, y),
    (x, y - 1),
    (x, y + 1))

  for d in dirs:
    if in_board(d) and (d != path[-1] if path else True):  # remove backwards movements
      if len(path) == 0 and board.get(cursor) == board.get(d):
        continue  # remove redundant first moves
      total_paths.extend(recurse_paths(d, newpath, depth, board))
  return total_paths


def solve_board(board, depth=5):
  solutions = []

  for x in range(6):
    for y in range(5):
      solutions.append(solve_position((x, y), board, depth=depth))
  return solutions


def solve_board_multithreaded(board, depth=5, workers=4):
  from multiprocessing import Process, Queue
  work_queue = Queue()
  done_queue = Queue()
  processes = []

  for x in range(6):
    for y in range(5):
      work_queue.put((x, y))

  for w in range(workers):
    p = Process(target=worker, args=(work_queue, done_queue, board, depth))
    processes.append(p)
    work_queue.put('STOP')
    p.start()

  for p in processes:
    p.join()

  done_queue.put('STOP')

  return list(iter(done_queue.get, 'STOP'))


def worker(work_queue, done_queue, board, depth):
  for start_pos in iter(work_queue.get, 'STOP'):
    done_queue.put(solve_position(start_pos, board, depth))

# TODO: memoization of solved board states
# TODO: cull end state redundant moves


def score_solution(path, combos, weights):
  return len(combos)


def solve_position(start_pos, board, depth=5):
  max_score = 0
  solution_path = None
  solution_combos = None

  for p in recurse_paths(start_pos, depth=depth, board=board):
    b = board.copy()
    combos = b.runpath(p).get_all_combos()
    score = score_solution(p, combos, None)

    if score > max_score:
      max_score = score
      solution_path = p
      solution_combos = combos

  return {
      'score': max_score,
      'path': solution_path,
      'combos': solution_combos
    }

if __name__ == '__main__':
  from models import Board
  board = Board.random_board(1)
  solutions = solve_board_multithreaded(board, depth=3, workers=1)

  from pprint import pprint
  pprint(solutions)
  print board