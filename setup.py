import cx_Freeze

# base = "Win32GUI" allows your application to open without a console window
executables = [cx_Freeze.Executable('main_copy.py', base = "Win32GUI")]

cx_Freeze.setup(
    name = "ChessOptima",
    options = {"build_exe" : 
        {"packages" : ["pygame", "stockfish"], "include_files" : ['chessassets/', 'chessassets/pieces/', 'chessassets/feedback_icons/', 'chessassets/stockfish-11-win/Windows/']}},
    executables = executables
)

