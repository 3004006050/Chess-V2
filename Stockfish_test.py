from stockfish import Stockfish


stockfish = Stockfish("stockfish-11-win\Windows\stockfish_20011801_32bit.exe") # pass in binary file location
stockfish.set_fen_position("rnbqkb1r/p2pn2p/5P2/1P4p1/1p3PP1/8/P2K3P/RNBQ1BNR w kq - 1 13")
print(stockfish.get_best_move())