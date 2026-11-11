"""Patterns library: named mating patterns and tactical motifs (/patterns/<slug>/). Same fields as traps.py, plus:
fen (optional start position for composed positions), flip (True = boards from Black's side), label (shown instead of the opening).
Every line is checked with python-chess; engine claims with Stockfish 17.1 (Nov 2026)."""

WINDMILL_GAME = ("d4 Nf6 Nf3 e6 Bg5 c5 e3 cxd4 exd4 Be7 Nbd2 d6 c3 Nbd7 Bd3 b6 Nc4 Bb7 Qe2 Qc7 O-O O-O Rfe1 Rfe8 Rad1 Nf8 Bc1 Nd5 Ng5 b5 Na3 b4 cxb4 Nxb4 "
                 "Qh5 Bxg5 Bxg5 Nxd3 Rxd3 Qa5 b4 Qf5 Rg3 h6 Nc4 Qd5 Ne3 Qb5 Bf6 Qxh5 Rxg7+ Kh8 Rxf7+ Kg8 Rg7+ Kh8 Rxb7+ Kg8 Rg7+ Kh8 Rg5+ Kh7 Rxh5")
BODEN_GAME = ("e4 e5 Nf3 d6 c3 f5 Bc4 Nf6 d4 fxe4 dxe5 exf3 exf6 Qxf6 gxf3 Nc6 f4 Bd7 Be3 O-O-O Nd2 Re8 Qf3 Bf5 O-O-O d5 Bxd5 Qxc3+ bxc3 Ba3#")
ZWI_GAME = "e4 e5 Nf3 Nc6 d4 exd4 Bc4 Nf6 e5 d5 Bb5 Ne4 Nxd4 Bd7 Nxc6 bxc6 Bd3 Bc5 Bxe4 Qh4 Qe2 dxe4"
ANAS_FEN = "2r2rk1/pp3ppp/8/3N4/8/3QR3/6PP/6K1 w - - 0 1"
STALE_FEN = "8/8/7K/3Q4/8/8/pk6/8 w - - 0 1"
STALE_MOVES = "Qd4+ Kb1 Qb4+ Kc2 Qa3 Kb1 Qb3+ Ka1 Kg5"

PATTERNS = [
    dict(slug="windmill", name="The Windmill", label="Tactic · discovered check", side="White wins", flip=False, mate=False,
         hook="One rook gives check six times, then takes the queen.",
         simple="A rook and a bishop aim at the same king. Every time the rook moves away, the bishop gives check. Every time the rook comes back, it gives check too. While the king is busy, the rook grabs a piece with each move, and at the end it takes the queen.",
         intro="Torre–Lasker, Moscow 1925. After 25.Bf6! Black cannot take the bishop, because the g-pawn is pinned by the rook on g3. So Black takes the queen on h5 instead: 25…Qxh5 26.Rxg7+ Kh8 27.Rxf7+ Kg8 28.Rg7+ Kh8 29.Rxb7+ Kg8 30.Rg7+ Kh8 31.Rg5+ Kh7 32.Rxh5. "
               "Six checks, and the last move takes the queen.",
         moves=WINDMILL_GAME,
         notes={0: ("START", "", "The most famous windmill in chess history. Step through the whole game."),
                48: ("BEFORE THE STORM", "24…Qb5", "Black's queen attacks White's queen on h5. White has a rook on g3 and a bishop on g5, both aimed at the king.", ["g3", "!g7", "!f7", "!b7"]),
                49: ("THE KEY MOVE", "25.Bf6!", "The bishop attacks g7 and h8. Taking it with the g-pawn is impossible: that pawn is pinned by the rook.", ["f6", "!g7"]),
                50: ("BLACK TAKES THE QUEEN", "25…Qxh5", "Black grabs White's queen. It does not stop the attack.", ["h5"]),
                51: ("CHECK 1", "26.Rxg7+", "The rook takes a pawn with check. The bishop on f6 protects it.", ["g7", "!h8"]),
                53: ("CHECK 2", "27.Rxf7+", "The rook leaves g7. That uncovers the bishop's check, and the rook takes another pawn.", ["f7"]),
                55: ("CHECK 3", "28.Rg7+", "The rook comes back to g7: check again.", ["g7"]),
                57: ("CHECK 4", "29.Rxb7+", "Now the rook takes a bishop with check.", ["b7"]),
                59: ("CHECK 5", "30.Rg7+", "Back to g7.", ["g7"]),
                61: ("CHECK 6", "31.Rg5+", "The last check, and the rook now looks at the queen.", ["g5", "!h5"]),
                63: ("THE QUEEN", "32.Rxh5", "The rook takes the queen. White is far ahead.", ["h5"])},
         fix=["To use it: find a rook that can check from a square where its next capture also gives check, and a second piece (bishop or queen) that gives check when the rook moves away.",
              "To stop it: don't let a bishop and a rook line up on your king's corner. Keep an extra defender (a piece on f6 or g6, or luft for the king) before the pieces arrive."],
         guide=[
             dict(h="Two pieces aim at one king", board=dict(moves=" ".join(WINDMILL_GAME.split()[:48]), arrows=["r:g3g7", "r:g5d8"], rings=["!g8"]), p=[
                 "White's rook on g3 and bishop on g5 both look at Black's king on g8. The windmill needs exactly this: two attackers that take turns giving check."]),
             dict(h="The quiet key move", board=dict(moves=" ".join(WINDMILL_GAME.split()[:49]), arrows=["y:g3g8", "r:f6h8"]), p=[
                 "25.Bf6 attacks g7 and h8. The g-pawn is pinned by the rook, so gxf6 is not allowed. Black's queen takes on h5, but nothing stops what comes next."]),
             dict(h="The windmill turns", board=dict(moves=" ".join(WINDMILL_GAME.split()[:57]), arrows=["r:f6h8"], rings=["!b7"]), p=[
                 "Each time the rook leaves g7, the bishop on f6 gives check. Each time it comes back, the rook gives check. In between it takes the pawns on g7 and f7 and the bishop on b7."]),
             dict(h="Six checks, then the queen", board=dict(moves=WINDMILL_GAME, rings=["h5"]), p=[
                 "The rook takes the queen on h5. Count: six checks, and the last move wins the queen."]),
         ],
         qa=[("Why can't Black take the bishop on f6?", "The g-pawn is pinned. The rook on g3 would give check on g8 as soon as the pawn moved, so gxf6 is illegal."),
             ("Are there other defences?", "Not good ones. After 25…g5 White plays 26.Qxh6 with mate in three, and after 25…Kh7 26.Rxg7+ also leads to mate in three. Taking the queen, as in the game, runs into the windmill."),
             ("Who played it?", "Carlos Torre of Mexico, against the former world champion Emanuel Lasker, Moscow 1925. It is the best-known example of this pattern."),
             ("What is the lesson?", "A discovered check is a free move: while your opponent answers the check, you can take something every time.")]),
    dict(slug="anastasias-mate", name="Anastasia's Mate", label="Mating pattern", side="White wins", flip=False, mate=True, fen=ANAS_FEN,
         hook="A knight, a rook and one queen sacrifice: mate on the edge.",
         simple="The knight on e7 takes away the king's escape squares on g8 and g6. The king's own pawn on g7 blocks the third. The queen gives herself up on h7 to pull the king onto the h-file, and the rook gives mate from h3.",
         intro="Position: White knight d5, queen d3, rook e3, king g1; Black king g8 with pawns on g7 and h7. 1.Ne7+ Kh8 (the only move) 2.Qxh7+ Kxh7 (the only move) 3.Rh3#. "
               "Without the queen sacrifice 2.Rh3 is not mate, because the pawn on h7 blocks the file and the king can stay on h8.",
         moves="Ne7+ Kh8 Qxh7+ Kxh7 Rh3#",
         notes={0: ("START", "", "A composed position that shows the pattern clearly. Step through the moves.", ["d5", "d3", "e3"]),
                1: ("THE KNIGHT", "1.Ne7+", "Check. The knight also covers g8 and g6.", ["e7", "!g8", "!g6"]),
                2: ("ONLY MOVE", "1…Kh8", "The king has nowhere else to go.", ["h8"]),
                3: ("THE SACRIFICE", "2.Qxh7+!", "The queen takes the pawn with check. It is protected by nothing, but the king has to take.", ["h7"]),
                4: ("ONLY MOVE", "2…Kxh7", "The king takes the queen. It is now on the h-file with no escape.", ["h7"]),
                5: ("MATE", "3.Rh3#", "The rook checks along the h-file. Its own pawn on g7 blocks the king, and the knight covers g8 and g6.", ["h3", "!h7"])},
         fix=["To use it: look for a knight that covers the squares next to the king, a rook (or queen) on an open file, and a pawn of the king's own that boxes it in.",
              "To stop it: don't leave the king in a corner with its own pawns around it and a rook-lift available. A flight square (like h6) or taking the knight first breaks it."],
         guide=[
             dict(h="The three ingredients", board=dict(fen=ANAS_FEN, moves="", arrows=["r:d5e7", "r:e3h3"], rings=["!g8", "!h7"]), p=[
                 "A knight that can jump to e7, a rook that can swing to h3, and a king in the corner with its own pawns on g7 and h7."]),
             dict(h="Knight check", board=dict(fen=ANAS_FEN, moves="Ne7+ Kh8", arrows=["r:e7g8", "r:e7g6"]), p=[
                 "1.Ne7+ forces the king to h8. From e7 the knight covers g8 and g6, so the king can't come back."]),
             dict(h="The queen sacrifice", board=dict(fen=ANAS_FEN, moves="Ne7+ Kh8 Qxh7+ Kxh7", arrows=["r:e3h3"]), p=[
                 "2.Qxh7+ drags the king onto the h-file. Taking the queen is the only legal move."]),
             dict(h="Mate", board=dict(fen=ANAS_FEN, moves="Ne7+ Kh8 Qxh7+ Kxh7 Rh3#", rings=["!h7"]), p=[
                 "3.Rh3 is checkmate. Remember it: knight, rook on the edge, and the king's own pawn that blocks."]),
         ],
         qa=[("Where does the name come from?", "From the novel Anastasia und das Schachspiel (1803) by Wilhelm Heinse."),
             ("Why is the queen sacrifice needed?", "Without it, 2.Rh3 is not mate: the pawn on h7 blocks the rook, and the king can stay on h8."),
             ("Is this from a real game?", "No. This is a composed position that shows the pattern in its clearest form.")]),
    dict(slug="bodens-mate", name="Boden's Mate", label="Mating pattern", side="Black wins", flip=True, mate=True,
         hook="Two bishops on crossing diagonals mate a king that hides behind its own pieces.",
         simple="The king has castled long, but its own pieces fill the squares around it. One bishop gives check from a3, and the other bishop on f5 covers the squares behind. Nothing can block the check and the king cannot step away.",
         intro="Schulder–Boden, London 1853. White's king is on c1 with its own rook on d1 and knight on d2 next to it. After 14.Bxd5? Qxc3+! 15.bxc3 Ba3# the bishop on a3 gives check, "
               "the bishop on f5 covers b1 and c2, and White's own pieces take the rest of the squares.",
         moves=BODEN_GAME,
         notes={0: ("START", "", "The game that made this mate famous. Step through the moves."),
                26: ("THE BAIT", "13…d5", "Black offers the pawn. White's king is already on c1.", ["d5"]),
                27: ("THE GREED", "14.Bxd5?", "White takes the pawn. It loses by force.", ["d5"]),
                28: ("QUEEN SACRIFICE", "14…Qxc3+!", "The queen takes on c3 with check.", ["c3", "!c1"]),
                29: ("FORCED", "15.bxc3", "The only legal move: the king cannot step away.", ["c3"]),
                30: ("MATE", "15…Ba3#", "Bishop a3 gives check. The bishop on f5 covers b1 and c2, and White's own rook and knight block d1 and d2.", ["a3", "!c1", "f5"])},
         fix=["To use it: look for two bishops (or a bishop and queen) on crossing diagonals aimed at a king that castled long, with its own pieces blocking the escape squares.",
              "To stop it: don't leave pawns and pieces glued around a castled king, and watch for a queen sacrifice that pulls a pawn away from b2."],
         guide=[
             dict(h="A king boxed in by its own pieces", board=dict(moves=" ".join(BODEN_GAME.split()[:27]), arrows=["r:f5c2", "r:f8a3"], rings=["!c1"]), p=[
                 "White's king on c1 has a rook on d1, a knight on d2 and pawns around it. The only open squares are guarded by Black's bishop on f5."]),
             dict(h="The queen sacrifice", board=dict(moves=" ".join(BODEN_GAME.split()[:28]), arrows=["r:c3c1"]), p=[
                 "14…Qxc3+ forces 15.bxc3. That pawn move opens the diagonal for the second bishop."]),
             dict(h="Bishop gives mate", board=dict(moves=BODEN_GAME, rings=["!c1"]), p=[
                 "15…Ba3 is checkmate. The two bishops work on crossing diagonals, one giving the check and the other taking away b1 and c2."]),
         ],
         qa=[("Why is it called Boden's Mate?", "It is named after Samuel Boden (1826–1882), who played it against Schulder in London in 1853. The game made the pattern famous, but it had appeared before."),
             ("Could White have avoided it?", "Yes. After 13…d5, moves like 14.Nb3 or 14.Rde1 only lose a piece, not the game. The real mistake was castling long on move 13: 13.Bd5 was better."),
             ("What is the lesson?", "A king hemmed in by its own pieces can be mated by two bishops. Count the flight squares before you castle long.")]),
    dict(slug="stalemate-trick", name="The Stalemate Trick", label="Endgame · saving a lost game", side="Black saves it", flip=False, mate=False, fen=STALE_FEN,
         hook="A queen down, and still a draw. The corner and the rook pawn do the work.",
         simple="Black has only a king and a pawn on the edge, one step from queening. White has a queen. If White's king is far away, Black keeps stepping into the corner, and White can never make progress without leaving Black no legal move. That is stalemate, and the game is drawn.",
         intro="Position: White king h6, queen d5; Black king b2, pawn a2. 1.Qd4+ Kb1 2.Qb4+ Kc2 3.Qa3 Kb1 4.Qb3+ Ka1. Now any king move is stalemate (5.Kg5 for example), and so are most queen moves. "
               "If White's king is close to the pawn, White wins by bringing the king over.",
         moves=STALE_MOVES,
         notes={0: ("START", "", "White is a whole queen up, but Black's pawn on a2 is a rook pawn and the white king is far away. Step through the moves.", ["a2", "a1"]),
                1: ("CHECK", "1.Qd4+", "Check along the long diagonal.", ["d4"]),
                2: ("KING RUNS", "1…Kb1", "Black runs toward the corner, next to the pawn.", ["b1"]),
                3: ("CHECK", "2.Qb4+", "White checks again.", ["b4"]),
                4: ("KING STEPS OUT", "2…Kc2", "Black steps out toward the middle.", ["c2"]),
                5: ("QUEEN WAITS", "3.Qa3", "White attacks the pawn.", ["a3", "!a2"]),
                6: ("BACK", "3…Kb1", "The king goes back to protect the pawn.", ["b1"]),
                7: ("CHECK", "4.Qb3+", "Check again.", ["b3"]),
                8: ("INTO THE CORNER", "4…Ka1", "Now Black's king is in the corner, next to the pawn. White to move.", ["a1"]),
                9: ("STALEMATE", "5.Kg5", "Any king move leaves Black with no legal move: stalemate, a draw.", ["a1"])},
         fix=["To use it: when you are lost and have a pawn on the a- or h-file one step from queening, bring your king to the corner next to it and keep making checks impossible to avoid.",
              "To avoid it: bring your own king closer first. With the king near the pawn the queen wins. And before you move, check whether your opponent will have a legal move."],
         guide=[
             dict(h="The setup", board=dict(fen=STALE_FEN, moves="", rings=["a2", "a1"]), p=[
                 "White has a whole queen, Black only a rook pawn on a2 and a king next to it. White's king is far away. That distance is what makes the draw possible."]),
             dict(h="Check and run", board=dict(fen=STALE_FEN, moves="Qd4+ Kb1 Qb4+ Kc2 Qa3 Kb1", arrows=["r:a3a2"]), p=[
                 "Black's king shuffles between b1, c2 and the corner. Every time White attacks the pawn, the king protects it again."]),
             dict(h="Stuck in the corner", board=dict(fen=STALE_FEN, moves="Qd4+ Kb1 Qb4+ Kc2 Qa3 Kb1 Qb3+ Ka1", rings=["!a1"]), p=[
                 "With the king on a1 and the pawn on a2, almost every White move leaves Black with no legal move."]),
             dict(h="Stalemate", board=dict(fen=STALE_FEN, moves=STALE_MOVES, rings=["!a1"]), p=[
                 "5.Kg5 and it is stalemate. A draw instead of a loss. Most queen moves are stalemate too."]),
         ],
         qa=[("Does this work with any pawn?", "No. It is the special trick of the rook pawn (a- or h-file) on the seventh rank. Against a central or knight's pawn the queen can still win."),
             ("What if White's king is close?", "Then White wins: the king walks over and helps to force the black king away. Without that help, the queen alone can't make progress."),
             ("What if White takes the pawn?", "In this position 5.Qxa2+ Kxa2 just loses the queen, because the king takes it."),
             ("What is the lesson?", "Never give up a lost game while a stalemate is possible, and never walk into one when you are winning.")]),
    dict(slug="zwischenzug", name="Zwischenzug", label="Tactic · the in-between move", side="Black wins", flip=True, mate=False,
         hook="Don't recapture on autopilot: a bigger threat first.",
         simple="Zwischenzug is German for \"in-between move\". Your opponent takes a piece, and you don't take back right away. You first make a move that creates a bigger threat. Your opponent has to deal with it, and then you take back anyway.",
         intro="Lichtenhein–Morphy, New York 1857. After 10.Bxe4 the normal reply is 10…dxe4, recapturing the bishop. Morphy first played 10…Qh4!, threatening 11…Qxf2#. "
               "White had to defend, for example with 11.Qe2, and only then did Black take on e4: 11…dxe4.",
         moves=ZWI_GAME,
         notes={0: ("START", "", "A zwischenzug from the first American Chess Congress. Step through the game.", []),
                19: ("THE EXPECTED MOVE", "10.Bxe4", "White's bishop takes Black's knight. Everyone expects 10…dxe4.", ["e4"]),
                20: ("IN-BETWEEN", "10…Qh4!", "Black doesn't take back. The queen threatens mate on f2.", ["h4", "!f2"]),
                21: ("FORCED", "11.Qe2", "White has to deal with the mate threat first.", ["e2"]),
                22: ("NOW TAKE BACK", "11…dxe4", "Black takes the piece back anyway.", ["e4"])},
         fix=["To use it: before you recapture, ask 'do I have a check, a mate threat or a capture that forces my opponent?' If yes, play it first. The recapture will still be there.",
              "To stop it: before you capture, check what your opponent can do besides taking back. Ask what their best forcing move is."],
         guide=[
             dict(h="The normal recapture", board=dict(moves=" ".join(ZWI_GAME.split()[:19]), arrows=["g:d5e4"]), p=[
                 "White's bishop has just taken on e4. Black can take it back with the d-pawn. That's the move everybody expects."]),
             dict(h="The in-between move", board=dict(moves=" ".join(ZWI_GAME.split()[:20]), arrows=["r:h4f2"]), p=[
                 "10…Qh4! attacks f2 and threatens mate in one. The bishop on c5 is the second attacker."]),
             dict(h="White must defend", board=dict(moves=" ".join(ZWI_GAME.split()[:21]), arrows=["g:d5e4"], rings=["e4"]), p=[
                 "11.Qe2 defends f2. The piece on e4 is still hanging, because Black never took it back."]),
             dict(h="Now recapture", board=dict(moves=ZWI_GAME, rings=["e4"]), p=[
                 "11…dxe4. Black takes the piece back after all. The in-between move came first."]),
         ],
         qa=[("Was 10…Qh4 the only good move?", "No. The simple recapture 10…dxe4 was also fine. The point of the example is the idea, not that one move is much stronger."),
             ("Why is it called Zwischenzug?", "It is German for \"in-between move\" (zwischen = between, Zug = move)."),
             ("When does it work?", "When your in-between move comes with check, a mate threat or a bigger capture, so your opponent has no time to do anything else.")]),
]
for _t in PATTERNS:
    _t.setdefault("opening", _t["label"])
for _t in PATTERNS:
    _t.setdefault("title", f'{_t["name"]}: how it works, step by step on the board')
    _t.setdefault("desc", _t["hook"] + " Step through every move on the board, with the plain-words explanation and how to use it.")
# rebuild trigger
# rebuild trigger 2
