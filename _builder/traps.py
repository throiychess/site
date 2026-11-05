"""Trap library: one entry per trap page (/traps/<slug>/). Every line is checked with python-chess (and Stockfish when written).
Fields: slug, name, opening, side, short (YouTube id, optional), hook (one line), simple (plain words, no notation),
intro (with notation), moves (SAN), mate (False if the line doesn't end in mate), notes {ply: (LABEL, tag, text, marks)}, fix [..].
marks: "e4" = white ring, "!e4" = red ring."""

TRAPS = [
    dict(slug="scholars-mate", name="Scholar's Mate", opening="King's Pawn Opening", side="White sets it", short="LCSXV_yJs_U",
         hook="Queen and bishop gang up on f7. Mate in four moves, unless you defend first.",
         simple="White points the queen and a bishop at one weak square next to Black's king. If Black doesn't defend it, the queen takes it and it's checkmate in four moves. Block the queen first, then chase it away.",
         intro="After 1.e4 e5 2.Bc4 Nc6 3.Qh5 both the queen and the bishop attack f7, a square only Black's king defends. "
               "The natural 3…Nf6?? attacks the queen but ignores the threat, and 4.Qxf7# is mate.",
         moves="e4 e5 Bc4 Nc6 Qh5 Nf6 Qxf7#",
         notes={0: ("START", "", "The fastest trap in chess. Step through the moves."),
                3: ("THE AIM", "2.Bc4", "White's bishop aims at f7, the weakest square next to Black's king.", ["c4", "!f7"]),
                5: ("THE THREAT", "3.Qh5", "The queen joins in. Queen and bishop both hit f7.", ["h5", "c4", "!f7"]),
                6: ("THE BLUNDER", "3…Nf6??", "The knight attacks the queen. Natural, but it ignores f7.", ["!f7"]),
                7: ("CHECKMATE", "4.Qxf7#", "Queen takes f7, protected by the bishop. Checkmate in four moves.", ["f7", "!e8"])},
         fix=["After Qh5, defend first: block with g6 or protect f7 with Qe7.",
              "Once f7 is safe, develop your knights and make the white queen run.",
              "An early queen is a target, not a danger, as long as you defend first."]),
    dict(slug="legals-mate", name="Légal's Mate", opening="Philidor Defense", side="White sets it", short="paGdwe1cYmk",
         hook="White gives away the queen and mates in two. Almost 300 years old, and it still works.",
         simple="White seems to give away the queen for free. If Black grabs it, three small pieces trap the black king and it's checkmate two moves later. Don't take the queen: take the knight instead. You lose a pawn, not the game.",
         intro="After 1.e4 e5 2.Nf3 d6 3.Bc4 Bg4 the bishop pins the knight to the queen. After the lazy 4.Nc3 g6? White ignores the pin: "
               "5.Nxe5! Bxd1?? 6.Bxf7+ Ke7 7.Nd5# is mate. Better is 5…dxe5, losing only a pawn.",
         moves="e4 e5 Nf3 d6 Bc4 Bg4 Nc3 g6 Nxe5 Bxd1 Bxf7+ Ke7 Nd5#",
         notes={0: ("START", "", "A trap from the 1700s. Step through the moves."),
                6: ("THE PIN", "3…Bg4", "Black's bishop pins the knight to the queen. Moving the knight seems to lose the queen.", ["g4", "!f3"]),
                8: ("LAZY MOVE", "4…g6?", "Black relaxes and plays a slow move."),
                9: ("THE BAIT", "5.Nxe5!", "White ignores the pin and leaves the queen hanging.", ["e5", "!d1"]),
                10: ("THE BLUNDER", "5…Bxd1??", "Black grabs the queen. Now White's small pieces strike."),
                11: ("CHECK", "6.Bxf7+", "Bishop takes f7, check. The king has only one square.", ["f7", "!e8"]),
                13: ("CHECKMATE", "7.Nd5#", "Knight d5. Three small pieces checkmate the king.", ["d5", "e5", "f7", "!e7"])},
         fix=["Don't grab the queen. Take the knight with 5…dxe5 instead.",
              "You lose a pawn, not the game. A free queen is never free when your king is in danger."]),
    dict(slug="fried-liver-attack", name="Fried Liver Attack", opening="Italian Game", side="White sets it", short="WFRx-dXjOcc",
         hook="White gives up a knight on f7 and drags Black's king into the middle of the board.", mate=False,
         simple="White sacrifices a knight to pull Black's king out of its safe spot. The king ends up in the middle of the board, where every white piece can attack it. Avoid it: don't take back in the center, attack the bishop with your knight instead.",
         intro="In the Two Knights Defense (1.e4 e5 2.Nf3 Nc6 3.Bc4 Nf6) White plays 4.Ng5 and attacks f7. After 4…d5 5.exd5 the natural 5…Nxd5? "
               "allows 6.Nxf7! Kxf7 7.Qf3+ Ke6 8.Nc3 and Black's king is stuck in the center. The fix is 5…Na5!",
         moves="e4 e5 Nf3 Nc6 Bc4 Nf6 Ng5 d5 exd5 Nxd5 Nxf7 Kxf7 Qf3+ Ke6 Nc3",
         notes={0: ("START", "", "One of the most famous attacks in chess. Step through the moves."),
                6: ("OPENING", "3…Nf6", "Two Knights Defense. Black attacks the e4 pawn."),
                7: ("THE ATTACK", "4.Ng5", "The knight jumps to g5. With the bishop it attacks f7.", ["g5", "c4", "!f7"]),
                9: ("OPENING", "5.exd5", "White takes on d5."),
                10: ("THE MISTAKE", "5…Nxd5?", "Taking back with the knight looks natural. It's the mistake.", ["!d5"]),
                11: ("THE SACRIFICE", "6.Nxf7!", "White gives up the knight on f7.", ["f7"]),
                12: ("FORCED", "6…Kxf7", "The king takes and leaves its shelter.", ["!f7"]),
                13: ("CHECK", "7.Qf3+", "Queen f3, check, and it also attacks the knight on d5.", ["f3", "!f7", "!d5"]),
                14: ("KING WALK", "7…Ke6", "The king walks into the center to protect the knight.", ["!e6"]),
                15: ("THE ATTACK", "8.Nc3", "Every white piece joins in. Black's king is stuck in the middle.", ["c3", "!e6"])},
         fix=["Don't take back on d5 with the knight. Play 5…Na5! and attack the bishop.",
              "A king in the center is a target. Keep it behind its pawns."]),
    dict(slug="fishing-pole-trap", name="Fishing Pole Trap", opening="Ruy Lopez", side="Black sets it", short="G2pqyA0mXF0",
         hook="Black leaves a knight hanging on g4. Take it, and the h-file opens straight onto your king.",
         simple="Black leaves a knight hanging right next to White's king. If White takes it, a whole column opens up towards the king, and Black's queen and rook give checkmate in the corner. Kicking the knight away is fine. Taking it is not.",
         intro="The Fishing Pole Trap is a sneaky idea for Black in the Ruy Lopez (1.e4 e5 2.Nf3 Nc6 3.Bb5 Nf6 4.O-O Ng4). "
               "After 5.h3 h5! the knight on g4 is offered as bait. If White takes it with 6.hxg4??, the h-file opens "
               "and Black's queen and rook deliver mate on h1.",
         moves="e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Ng4 h3 h5 hxg4 hxg4 Nh2 Qh4 f3 g3 Rf2 Nd4 Kf1 gxh2 Ke1 h1=Q+ Bf1 Qxf1+ Kxf1 Qh1#",
         notes={0: ("START", "", "The Fishing Pole starts from a normal Ruy Lopez. Step through the moves."),
                6: ("OPENING", "3…Nf6", "A normal Ruy Lopez. Nothing special yet."),
                7: ("OPENING", "4.O-O", "White castles. The king goes to g1."),
                8: ("OPENING", "4…Ng4", "Black's knight jumps to g4. It looks silly, and that is the point."),
                9: ("THE KICK", "5.h3", "White kicks the knight. A good move, as long as White doesn't take it later.", ["h3"]),
                10: ("THE BAIT", "5…h5!", "Black ignores the threat and leaves the knight. That's the bait.", ["!g4"]),
                11: ("THE BLUNDER", "6.hxg4??", "A free knight? Taking it is the real blunder.", ["!g4"]),
                12: ("THE OPEN FILE", "6…hxg4", "The h-file is open. The rook on h8 now aims at the king.", ["h8", "!g1"]),
                13: ("THE OPEN FILE", "7.Nh2", "The knight runs away from g4's pawn."),
                14: ("MATE THREAT", "7…Qh4!", "Queen and rook are lined up on the h-file. Qh1 mate is coming.", ["h4", "h8"]),
                15: ("MATE THREAT", "8.f3", "White makes room so the king can escape via f2."),
                16: ("MATE THREAT", "8…g3!", "g3 locks the king in. Now only Rf2 or Re1 stop mate in one, and they only delay it.", ["g3", "!g1"]),
                17: ("NO WAY OUT", "9.Rf2", "The rook covers f2. Black keeps piling on."),
                26: ("CHECKMATE", "13…Qh1#", "The king tried to run, but the attack is too strong. Checkmate on h1.", ["!f1", "h1"])},
         fix=["If the knight is left hanging after …h5, don't take it. The open h-file is worth more than a knight.",
              "Kicking the knight with h3 is fine. The mistake comes one move later.",
              "Your king hides behind f2, g2 and h2. Keep them home and keep developing.",
              "As Black it is a cheeky blitz trick. It only works if they bite, so don't count on it."]),
    dict(slug="petrov-trap", name="Petrov Trap", opening="Petrov Defense", side="White sets it", short="KA_x11CO7Gg",
         hook="Copy White's moves in the Petrov and one knight jump wins your queen.", mate=False,
         simple="Black copies White's moves, and that is the problem. White's queen and Black's king end up on the same line, so one knight jump gives check and attacks Black's queen at the same time. Kick the knight away first, then take back your pawn.",
         intro="After 1.e4 e5 2.Nf3 Nf6 3.Nxe5 copying with 3…Nxe4? is risky: 4.Qe2! pins the knight. If it runs with 4…Nf6?? then 5.Nc6+ "
               "is a discovered check that also attacks the queen. The fix is 3…d6 first, then take on e4.",
         moves="e4 e5 Nf3 Nf6 Nxe5 Nxe4 Qe2 Nf6 Nc6+ Qe7 Nxe7 Bxe7",
         notes={0: ("START", "", "A trap that punishes copying. Step through the moves."),
                4: ("OPENING", "2…Nf6", "The Petrov Defense: Black copies White."),
                5: ("OPENING", "3.Nxe5", "White takes the e5 pawn."),
                6: ("THE MISTAKE", "3…Nxe4?", "Black copies again and takes e4.", ["!e4"]),
                7: ("THE PIN", "4.Qe2!", "The queen attacks the knight and lines up with Black's king.", ["e2", "!e4", "!e8"]),
                8: ("THE BLUNDER", "4…Nf6??", "The knight runs away and opens the line to the king."),
                9: ("DISCOVERED CHECK", "5.Nc6+", "The knight jumps away: check from the queen, and the knight attacks Black's queen.", ["c6", "e2", "!d8", "!e8"]),
                11: ("QUEEN LOST", "6.Nxe7", "Black has to block the check, and White wins the queen.", ["e7"])},
         fix=["Play 3…d6 first. Kick the knight, then take on e4.",
              "Copying your opponent is not a plan. Check what their pieces can do."]),
    dict(slug="blackburne-shilling-gambit", name="Blackburne Shilling Gambit", opening="Italian Game", side="Black sets it",
         hook="Black hangs a pawn on purpose. Grab it, get greedy, and it's mate on move seven.",
         simple="Black leaves a pawn hanging on purpose. If White grabs it and then goes for even more, Black's queen crashes in and a knight gives checkmate. Don't take the pawn: castle, or take Black's knight.",
         intro="After 1.e4 e5 2.Nf3 Nc6 3.Bc4 Nd4?! the e5 pawn is loose. 4.Nxe5? Qg5! hits the knight and g2, and after the greedy 5.Nxf7?? "
               "Qxg2 6.Rf1 Qxe4+ 7.Be2 Nf3# is mate. Simply 4.O-O or 4.Nxd4 is good for White.",
         moves="e4 e5 Nf3 Nc6 Bc4 Nd4 Nxe5 Qg5 Nxf7 Qxg2 Rf1 Qxe4+ Be2 Nf3#",
         notes={0: ("START", "", "A cheeky trap with a famous name. Step through the moves."),
                6: ("THE BAIT", "3…Nd4?!", "The knight jumps to d4 and leaves the e5 pawn hanging.", ["d4", "!e5"]),
                7: ("THE GREED", "4.Nxe5?", "White grabs the pawn.", ["e5"]),
                8: ("COUNTERATTACK", "4…Qg5!", "The queen attacks the knight on e5 and the pawn on g2.", ["g5", "!e5", "!g2"]),
                9: ("THE BLUNDER", "5.Nxf7??", "White goes for more: queen and rook are both attacked. Too slow.", ["f7"]),
                10: ("ATTACK", "5…Qxg2", "Queen takes g2 and attacks the rook.", ["g2", "!h1"]),
                12: ("CHECK", "6…Qxe4+", "Queen takes e4, check.", ["e4", "!e1"]),
                13: ("BLOCK", "7.Be2", "The bishop blocks, and the king is boxed in."),
                14: ("CHECKMATE", "7…Nf3#", "Knight f3. Checkmate.", ["f3", "!e1"])},
         fix=["Don't take on e5. Castle, or take the knight on d4.",
              "If you did take and the queen comes to g5, don't grab more: castle (your king then covers g2) and give the knight back.",
              "A free pawn that opens lines to your king is not free."]),
    dict(slug="stafford-gambit", name="Stafford Gambit", opening="Petrov Defense", side="Black sets it", short="TsHaDaBUS-c",
         hook="Black gives away the queen on purpose. Take it, and it's mate in two.",
         simple="Black gives away the queen on purpose. If White takes it, Black's bishops and knight checkmate White's king two moves later. Before you grab a queen, check every check your opponent has.",
         intro="After 1.e4 e5 2.Nf3 Nf6 3.Nxe5 Nc6 4.Nxc6 dxc6 5.d3 Bc5 the bishop aims at f2. 6.Bg5?? looks active, but 6…Nxe4! 7.Bxd8 Bxf2+ 8.Ke2 Bg4# is mate. "
               "Simple development with Be2 and castling is good for White.",
         moves="e4 e5 Nf3 Nf6 Nxe5 Nc6 Nxc6 dxc6 d3 Bc5 Bg5 Nxe4 Bxd8 Bxf2+ Ke2 Bg4#",
         notes={0: ("START", "", "A famous blitz trap. Step through the moves."),
                6: ("THE GAMBIT", "3…Nc6", "Black gives up a pawn for fast development."),
                10: ("THE AIM", "5…Bc5", "The bishop aims straight at f2, next to White's king.", ["c5", "!f2"]),
                11: ("THE MISTAKE", "6.Bg5??", "White pins the knight and attacks the queen.", ["g5", "!d8"]),
                12: ("THE BAIT", "6…Nxe4!", "Black ignores the threat to the queen.", ["e4", "!d8"]),
                13: ("THE BLUNDER", "7.Bxd8??", "White takes the queen."),
                14: ("CHECK", "7…Bxf2+", "Bishop takes f2, check. The king must go to e2.", ["f2", "!e1"]),
                16: ("CHECKMATE", "8…Bg4#", "Bishop g4. Checkmate.", ["g4", "!e2"])},
         fix=["Don't play Bg5. Develop with Be2 and castle.",
              "Before you grab a queen, check every check.",
              "f2 is weak in the opening. Watch out for bishops aiming at it."]),
    dict(slug="halloween-gambit", name="Halloween Gambit", opening="Four Knights Game", side="White sets it",
         hook="White gives away a knight on move four. Scary? Not if you know the one safe square.", mate=False,
         simple="White gives away a whole knight to chase Black's knights with pawns. One knight ends up with only one safe square: all the way back home. Every other square gets it captured. Then don't sit and wait: strike back in the center, give a pawn back and get your pieces out. You stay a piece up.",
         intro="After 1.e4 e5 2.Nf3 Nc6 3.Nc3 Nf6 White plays 4.Nxe5!?, a knight for a pawn. After 4…Nxe5 5.d4 Ng6 6.e5 the knight on f6 is attacked: "
               "Ne4, Nd5, Ng4 and Nh5 all get taken, so 6…Ng8 is the only good move. After 7.Bc4 Black strikes back with 7…d5! 8.Bxd5 N8e7 and is clearly better (Stockfish about -1.9).",
         moves="e4 e5 Nf3 Nc6 Nc3 Nf6 Nxe5 Nxe5 d4 Ng6 e5 Ng8 Bc4 d5 Bxd5 N8e7",
         notes={0: ("START", "", "A scary-looking gambit in the Four Knights. Step through the moves."),
                6: ("OPENING", "3…Nf6", "The Four Knights Game. Quiet so far."),
                7: ("THE GAMBIT", "4.Nxe5!?", "White gives away a knight for one pawn.", ["e5"]),
                8: ("THE GAMBIT", "4…Nxe5", "Black takes. Now White's pawns start chasing."),
                9: ("THE CHASE", "5.d4", "The pawn attacks the knight. The knight must run.", ["d4", "!e5"]),
                10: ("THE CHASE", "5…Ng6", "The knight runs to g6."),
                11: ("THE CATCH", "6.e5", "The other knight is attacked. Every square forward gets taken. Staying gets taken too.", ["e5", "!f6"]),
                12: ("THE CATCH", "6…Ng8!", "The only safe move: back home. Black is a knight up, but nothing is developed.", ["g8"]),
                13: ("THE RESULT", "7.Bc4", "White has a big center and the bishop aims at f7.", ["c4", "!f7"]),
                14: ("THE FIX", "7…d5!", "Strike back in the center. It attacks the bishop.", ["d5"]),
                15: ("THE FIX", "8.Bxd5", "White wins a pawn back…"),
                16: ("THE FIX", "8…N8e7", "…and Black develops. Black is still a piece up and clearly better.", ["e7"])},
         fix=["When the knight on f6 is attacked by the pawn, go back to g8. Every other square loses the knight.",
              "Then strike back with …d5. Give a pawn back and develop fast.",
              "Against any gambit: don't hold on to everything. Your extra piece wins in the end."]),
    dict(slug="englund-gambit", name="Englund Gambit", opening="Englund Gambit", side="Black sets it",
         hook="Black gives a pawn on move one. Chase the queen the wrong way and it's mate on your back rank.",
         simple="Black throws away a pawn on move one and brings the queen out early. If White chases the queen the wrong way, the row behind White's king is left empty, and the queen gives checkmate there. Develop your knight instead and keep that row covered.",
         intro="Black gives up a pawn and brings the queen out early to win it back. The queen then grabs the pawn on b2. "
               "If White chases it with the bishop on c3, Black pins that bishop and a few moves later the queen gives checkmate on c1. "
               "Moving the knight to c3 instead keeps everything safe. The full guide below shows it step by step.",
         moves="d4 e5 dxe5 Nc6 Nf3 Qe7 Bf4 Qb4+ Bd2 Qxb2 Bc3 Bb4 Qd2 Bxc3 Qxc3 Qc1#",
         notes={0: ("START", "", "A trap against 1.d4. Step through the moves."),
                2: ("THE GAMBIT", "1…e5", "Black gives away a pawn on move one.", ["e5"]),
                6: ("OPENING", "3…Qe7", "The queen comes out early to win the pawn back."),
                8: ("CHECK", "4…Qb4+", "Queen b4, check, and it also hits b2.", ["b4", "!b2"]),
                10: ("THE GRAB", "5…Qxb2", "The queen grabs b2 and attacks the rook.", ["b2", "!a1"]),
                11: ("THE BLUNDER", "6.Bc3??", "White attacks the queen, but leaves c1 unguarded.", ["c3", "!c1"]),
                12: ("THE PIN", "6…Bb4!", "Bishop b4. White's queen has to defend.", ["b4", "!c3"]),
                15: ("EMPTY BACK RANK", "8.Qxc3", "The queen takes back. Nothing guards c1 anymore.", ["!c1"]),
                16: ("CHECKMATE", "8…Qc1#", "Queen c1. Checkmate on the back rank.", ["c1", "!e1"])},
         fix=["After the queen takes b2, play Nc3, not Bc3.",
              "Keep your back rank covered when the enemy queen is close to it."],
         # Guide below the board: plain words, a board with arrows per step (g = good move, r = threat). Lines checked with Stockfish 17.1 (4 Nov 2026).
         title="Englund Gambit: the trap, the refutation and how to beat it",
         desc="How to beat the Englund Gambit, step by step on the board: take the pawn, bring your pieces out, and never attack the queen with your bishop on c3.",
         guide=[
             dict(h="Black gives away a pawn", board=dict(moves="d4 e5", arrows=["g:d4e5"]), p=[
                 "White moves the queen's pawn two squares. Black puts a pawn right next to it, where White can simply take it. That is the Englund Gambit: a free pawn on the very first move.",
                 "It is named after the Swedish player Fritz Englund."]),
             dict(h="Step 1: take the pawn", board=dict(moves="d4 e5 dxe5 Nc6", arrows=["r:c6e5", "g:g1f3"]), p=[
                 "Yes, take it. That is the best move. Black's knight now attacks your pawn.",
                 "Protect it by bringing your knight out (green arrow). Your pawn is safe and your knight is in the game."]),
             dict(h="Step 2: the queen comes out", board=dict(moves="d4 e5 dxe5 Nc6 Nf3 Qe7", arrows=["r:e7e5", "g:c1f4"]), p=[
                 "Black's queen joins the attack on your pawn. No need to worry. Keep bringing pieces out.",
                 "Your bishop goes to f4 and protects the pawn a second time."]),
             dict(h="Step 3: check! Block with the bishop", board=dict(moves="d4 e5 dxe5 Nc6 Nf3 Qe7 Bf4 Qb4+", arrows=["r:b4e1", "r:b4f4", "r:b4b2", "g:f4d2"]), p=[
                 "The queen gives check, and at the same time it attacks your bishop and the pawn on b2.",
                 "Block the check with the bishop: back to d2 (green arrow). Now the check is gone and your bishop is safe.",
                 "Careful: if you block with a pawn or with your other knight, the queen just takes your bishop on f4."]),
             dict(h="Step 4: the queen grabs a pawn", board=dict(moves="d4 e5 dxe5 Nc6 Nf3 Qe7 Bf4 Qb4+ Bd2 Qxb2", arrows=["r:b2a1", "g:b1c3"]), p=[
                 "The queen takes the pawn on b2 and attacks your rook in the corner.",
                 "Play your knight to c3 (green arrow). Now your queen protects the rook, your back row is covered, and Black's queen is far from home. You are a pawn up and doing great."]),
             dict(h="The trap: don't chase the queen with your bishop", board=dict(moves="d4 e5 dxe5 Nc6 Nf3 Qe7 Bf4 Qb4+ Bd2 Qxb2 Bc3 Bb4", arrows=["r:b4c3", "r:b2c3"]), p=[
                 "Attacking the queen with the bishop on c3 looks smart. It is the mistake Black is waiting for.",
                 "Black's bishop comes to b4. Now your bishop is pinned: it can't move, because your king stands right behind it. Two black pieces attack it and you can't hold everything together. You lose material, and it can get even worse."]),
             dict(h="How the trap ends", board=dict(moves="d4 e5 dxe5 Nc6 Nf3 Qe7 Bf4 Qb4+ Bd2 Qxb2 Bc3 Bb4 Qd2 Bxc3 Qxc3 Qc1#", arrows=["r:c1e1"], rings=["!e1"]), p=[
                 "If White protects the bishop with the queen, Black takes on c3, White takes back, and the black queen jumps to c1. Checkmate: nothing guards White's back row.",
                 "The lesson: when the enemy queen is on your side of the board, keep your back row covered. The knight on c3 does exactly that."]),
         ],
         qa=[
             ("Should I take the pawn?", "Yes. Taking the pawn is the best answer. Then defend it with your pieces and remember the one trap."),
             ("What is the one thing to remember?", "When Black's queen takes the pawn on b2, move your knight to c3. Never attack the queen with your bishop on c3."),
             ("Is the Englund Gambit a good opening for Black?", "Not really. If White plays normal moves, White simply stays a pawn up. It only works as a surprise against someone who doesn't know the trap."),
         ]),
    dict(slug="elephant-trap", name="Elephant Trap", opening="Queen's Gambit Declined", side="Black sets it",
         hook="The d5 pawn looks free. Grab it and you lose a whole piece.", mate=False,
         simple="A pawn looks free because the knight defending it seems stuck. It isn't. If White grabs the pawn, Black gives the queen, wins it straight back with check and ends up a whole piece ahead. Count the pieces before you grab.",
         intro="After 1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5 Nbd7 5.cxd5 exd5 the pawn on d5 looks loose because the knight on f6 is pinned. "
               "6.Nxd5?? Nxd5! 7.Bxd8 Bb4+ 8.Qd2 Bxd2+ 9.Kxd2 Kxd8 leaves Black a piece up. Simply 6.e3 is fine.",
         moves="d4 d5 c4 e6 Nc3 Nf6 Bg5 Nbd7 cxd5 exd5 Nxd5 Nxd5 Bxd8 Bb4+ Qd2 Bxd2+ Kxd2 Kxd8",
         notes={0: ("START", "", "A classic in the Queen's Gambit. Step through the moves."),
                7: ("THE PIN", "4.Bg5", "White pins the knight on f6 to the queen.", ["g5", "!f6", "!d8"]),
                8: ("THE SETUP", "4…Nbd7", "Black's other knight goes to d7.", ["d7"]),
                10: ("THE BAIT", "5…exd5", "The d5 pawn now looks loose.", ["!d5"]),
                11: ("THE GREED", "6.Nxd5??", "White grabs the pawn, trusting the pin.", ["d5"]),
                12: ("SURPRISE", "6…Nxd5!", "The pin isn't real. Black takes back and offers the queen.", ["d5", "!d8"]),
                13: ("QUEEN GRAB", "7.Bxd8", "White takes the queen…"),
                14: ("CHECK", "7…Bb4+", "…but bishop b4 is check. Only the queen can block.", ["b4", "!e1"]),
                16: ("QUEEN BACK", "8…Bxd2+", "Black wins the queen back, with check."),
                18: ("PIECE UP", "9…Kxd8", "The queens are gone and Black is a whole piece up.", ["d8"])},
         fix=["A pinned knight can still move if it wins something bigger. Check that first.",
              "Don't take on d5 here. Just develop with e3."]),
    dict(slug="lasker-trap", name="Lasker Trap", opening="Albin Counter-Gambit", side="Black sets it",
         hook="A pawn marches all the way and turns into a knight, with check.", mate=False,
         simple="Black pushes a pawn deep into White's position. If White grabs a bishop, that pawn keeps capturing, reaches the last row and turns into a knight with check. White's position falls apart. Bring your knight out early instead.",
         intro="After 1.d4 d5 2.c4 e5 3.dxe5 d4 the pawn on d4 cramps White. 4.e3? Bb4+ 5.Bd2 dxe3! 6.Bxb4?? exf2+ 7.Ke2 fxg1=N+! "
               "is a famous underpromotion. 4.Nf3 is the better move.",
         moves="d4 d5 c4 e5 dxe5 d4 e3 Bb4+ Bd2 dxe3 Bxb4 exf2+ Ke2 fxg1=N+",
         notes={0: ("START", "", "A rare trap with a rare promotion. Step through the moves."),
                4: ("THE GAMBIT", "2…e5", "The Albin Counter-Gambit. Black offers a pawn.", ["e5"]),
                6: ("THE WEDGE", "3…d4", "The pawn pushes into White's half of the board.", ["d4"]),
                7: ("THE MISTAKE", "4.e3?", "White attacks the pawn. It's the first mistake.", ["e3"]),
                8: ("CHECK", "4…Bb4+", "Bishop b4, check.", ["b4", "!e1"]),
                9: ("BLOCK", "5.Bd2", "White blocks."),
                10: ("THE BAIT", "5…dxe3!", "Black ignores the bishop and takes on e3.", ["e3"]),
                11: ("THE BLUNDER", "6.Bxb4??", "White grabs the bishop."),
                12: ("CHECK", "6…exf2+", "Pawn takes f2, check. The king has to move.", ["f2", "!e1"]),
                14: ("UNDERPROMOTION", "7…fxg1=N+!", "The pawn becomes a knight, with check. Not a queen: a knight. White's position falls apart.", ["g1", "!e2"])},
         fix=["Play 4.Nf3 instead of e3.",
              "When an enemy pawn is that close to your king, deal with the pawn before you grab anything."]),
    dict(slug="siberian-trap", name="Siberian Trap", opening="Smith-Morra Gambit", side="Black sets it",
         hook="Queen and knight aim at h2. Kick the knight and it's mate in two.",
         simple="Black's queen and knight both aim at the square next to White's king. If White kicks the knight and then takes the bait, the only defender of that square disappears and the queen gives checkmate. Don't kick the knight. Keep developing, for example by attacking the queen with your other knight.",
         intro="In the Smith-Morra Gambit (1.e4 c5 2.d4 cxd4 3.c3 dxc3 4.Nxc3) Black sets up with …Qc7 and …Ng4, both aiming at h2. "
               "After 9.h3?? Nd4! the queen is attacked, and 10.Nxd4 Qh2# is mate. 9.Nb5 chases the queen away.",
         moves="e4 c5 d4 cxd4 c3 dxc3 Nxc3 Nc6 Nf3 e6 Bc4 Qc7 O-O Nf6 Qe2 Ng4 h3 Nd4 Nxd4 Qh2#",
         notes={0: ("START", "", "A trap against the Smith-Morra Gambit. Step through the moves."),
                5: ("THE GAMBIT", "3.c3", "White offers pawns for fast development."),
                12: ("THE AIM", "6…Qc7", "Black's queen sits on c7 and aims at h2.", ["c7", "!h2"]),
                16: ("THE KNIGHT", "8…Ng4", "The knight jumps to g4. Queen and knight both aim at h2.", ["g4", "c7", "!h2"]),
                17: ("THE BLUNDER", "9.h3??", "White kicks the knight. It looks natural.", ["h3"]),
                18: ("THE BAIT", "9…Nd4!", "The other knight attacks White's queen.", ["d4", "!e2"]),
                19: ("NO DEFENDER", "10.Nxd4", "The knight on f3 takes, but it was the only defender of h2.", ["!h2"]),
                20: ("CHECKMATE", "10…Qh2#", "Queen h2. Checkmate.", ["h2", "!g1"])},
         fix=["Don't play h3. Nb5 (attacking the queen) or Rd1 keeps a good game.",
              "When two pieces aim at the square next to your king, keep its defender in place."]),
]

# ---------------------------------------------------------------------------------------------
# Step-by-step guides below the board (same format as the Englund entry above).
# Plain words, no engine numbers. Arrows: "g:" = a good move/idea for you, "r:" = a threat.
# "You" = the side that must avoid the trap; boards are shown from that side.
# Every green move and every claim was checked with Stockfish 17.1 (depth 18-20) on 5 Nov 2026.
GUIDES = {
    "scholars-mate": dict(
        title="Scholar's Mate: how to stop the 4-move checkmate",
        desc="How to stop Scholar's Mate, step by step on the board: see the threat on f7, defend first, then chase the queen away.",
        guide=[
            dict(h="White aims at f7", board=dict(moves="e4 e5 Bc4", arrows=["r:c4f7"]), p=[
                "White's bishop points at f7, the square next to your king. At the start only your king protects it."]),
            dict(h="The queen joins in", board=dict(moves="e4 e5 Bc4 Nc6 Qh5", arrows=["r:h5f7", "r:c4f7"]), p=[
                "Now the queen and the bishop both attack f7. If you don't defend it, the queen takes on f7 with checkmate."]),
            dict(h="The mistake", board=dict(moves="e4 e5 Bc4 Nc6 Qh5 Nf6 Qxf7#", rings=["!e8"]), p=[
                "Bringing the knight to f6 attacks the queen, so it feels active. But it does nothing for f7.",
                "The queen takes on f7, protected by the bishop, and your king can't take back. Checkmate."]),
            dict(h="The fix: defend first", board=dict(moves="e4 e5 Bc4 Nc6 Qh5", arrows=["g:g7g6", "g:d8e7"]), p=[
                "Block the queen's line with the pawn in front of your bishop (to g6), or protect f7 with your queen (to e7). Both are good moves."]),
            dict(h="Then make the queen run", board=dict(moves="e4 e5 Bc4 Nc6 Qh5 g6 Qf3 Nf6", arrows=["r:f3f7", "g:f8g7"]), p=[
                "After g6 the queen often comes back to f3 and aims at f7 again. Your knight on f6 blocks that line and develops at the same time.",
                "Now bring out your other pieces. Every time the queen has to move again, you win time."]),
        ],
        qa=[("How do I stop Scholar's Mate?", "When the queen and bishop both aim at f7, defend that square before you do anything else: pawn to g6 or queen to e7."),
            ("Is it bad for White to bring the queen out so early?", "If you defend correctly, yes. The queen gets chased around while you develop your pieces with every move.")]),
    "legals-mate": dict(
        title="Légal's Mate: the queen sacrifice trap and how to avoid it",
        desc="How Légal's Mate works and how to avoid it, step by step on the board: why the free queen is bait and which piece to take instead.",
        guide=[
            dict(h="Your bishop pins the knight", board=dict(moves="e4 e5 Nf3 d6 Bc4 Bg4", arrows=["y:g4d1"]), p=[
                "Your bishop stands in front of White's knight, with White's queen behind it. If the knight moves away, the queen seems to be yours."]),
            dict(h="The slow move", board=dict(moves="e4 e5 Nf3 d6 Bc4 Bg4 Nc3", arrows=["g:b8c6", "g:g8f6"]), p=[
                "Here a pawn move to g6 is too slow. Bring out a knight instead. That keeps the pawn on e5 protected and your pieces ready."]),
            dict(h="The bait", board=dict(moves="e4 e5 Nf3 d6 Bc4 Bg4 Nc3 g6 Nxe5", arrows=["r:e5f7", "r:c4f7"]), p=[
                "After the slow move, the knight jumps away anyway and takes your pawn. White's queen is left for you to take.",
                "Look at f7: the bishop and the knight both aim at it. That is the real threat."]),
            dict(h="Take the queen and it's mate", board=dict(moves="e4 e5 Nf3 d6 Bc4 Bg4 Nc3 g6 Nxe5 Bxd1 Bxf7+ Ke7 Nd5#", rings=["!e7"]), p=[
                "If you take the queen, the bishop checks on f7, your king has to go to e7, and the knight lands on d5. Checkmate with three small pieces."]),
            dict(h="The fix: take the knight", board=dict(moves="e4 e5 Nf3 d6 Bc4 Bg4 Nc3 g6 Nxe5", arrows=["g:d6e5"]), p=[
                "Take the knight with your pawn. White's queen then takes your bishop, so you end up a pawn down and White is better. That is still much better than getting mated."]),
        ],
        qa=[("Should I take the queen in Légal's Mate?", "No. Take the knight with your pawn instead. A free queen is never free when your king is in danger."),
            ("How do I avoid getting into this position?", "Don't play slow pawn moves while White's pieces aim at f7. Bring out your knights first.")]),
    "fried-liver-attack": dict(
        title="Fried Liver Attack: how to stop it as Black",
        desc="How to stop the Fried Liver Attack, step by step on the board: the move to play instead of taking back on d5, and why your king must stay home.",
        guide=[
            dict(h="The knight attacks f7", board=dict(moves="e4 e5 Nf3 Nc6 Bc4 Nf6 Ng5", arrows=["r:g5f7", "r:c4f7"]), p=[
                "White's knight jumps to g5. Together with the bishop it attacks f7, the square next to your king."]),
            dict(h="Block with the d-pawn", board=dict(moves="e4 e5 Nf3 Nc6 Bc4 Nf6 Ng5", arrows=["g:d7d5"]), p=[
                "Push the pawn in front of your queen two squares. It blocks the bishop's line to f7."]),
            dict(h="Don't take back with the knight", board=dict(moves="e4 e5 Nf3 Nc6 Bc4 Nf6 Ng5 d5 exd5", arrows=["g:c6a5"]), p=[
                "White takes your pawn. Taking back with the knight looks natural, but it's the mistake.",
                "Move your other knight to a5 instead. It attacks the bishop, so White has to deal with that first."]),
            dict(h="What happens if you take back", board=dict(moves="e4 e5 Nf3 Nc6 Bc4 Nf6 Ng5 d5 exd5 Nxd5 Nxf7 Kxf7 Qf3+", arrows=["r:f3f7", "r:f3d5"]), p=[
                "White gives up the knight on f7. Your king has to take it, and the queen gives check while attacking your knight on d5."]),
            dict(h="The king in the middle", board=dict(moves="e4 e5 Nf3 Nc6 Bc4 Nf6 Ng5 d5 exd5 Nxd5 Nxf7 Kxf7 Qf3+ Ke6 Nc3", arrows=["r:c3d5", "r:c4d5", "r:f3d5"], rings=["!e6"]), p=[
                "Your king walks to e6 to protect the knight. Now every white piece joins in, and your king has no safe place to go."]),
        ],
        qa=[("What is the best answer to the Fried Liver Attack?", "Don't let it happen: after White takes on d5, move your knight from c6 to a5 and attack the bishop."),
            ("Is the knight sacrifice on f7 really that dangerous?", "Yes. Your king gets pulled into the middle of the board, where White's pieces can attack it from every side.")]),
    "fishing-pole-trap": dict(
        title="Fishing Pole Trap: how it works and how to avoid it",
        desc="How the Fishing Pole Trap works and how to avoid it, step by step on the board: why the knight on g4 is bait and what to play instead.",
        guide=[
            dict(h="A strange knight jump", board=dict(moves="e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Ng4", arrows=["g:h2h3"]), p=[
                "Black's knight jumps to g4. It looks odd. Kicking it with the h-pawn is a good move."]),
            dict(h="The bait", board=dict(moves="e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Ng4 h3 h5", rings=["!g4"]), p=[
                "Black doesn't move the knight. Instead the h-pawn comes forward too. The knight on g4 is now free to take, and that is the bait."]),
            dict(h="Don't take it", board=dict(moves="e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Ng4 h3 h5", arrows=["g:c2c3", "g:d2d4"]), p=[
                "Leave the knight alone and keep playing normal moves, like the c-pawn or d-pawn forward. You stay clearly better."]),
            dict(h="Take it and the h-file opens", board=dict(moves="e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Ng4 h3 h5 hxg4 hxg4 Nh2 Qh4", arrows=["r:h4h2", "r:h8h4"]), p=[
                "If you take the knight, Black takes back with the pawn and the h-file is open. The black queen and rook line up on it, aiming at your king."]),
            dict(h="How it ends", board=dict(moves="e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Ng4 h3 h5 hxg4 hxg4 Nh2 Qh4 f3 g3 Rf2 Nd4 Kf1 gxh2 Ke1 h1=Q+ Bf1 Qxf1+ Kxf1 Qh1#", rings=["!f1"]), p=[
                "Your king tries to run, but the attack is too strong. Checkmate on h1."]),
        ],
        qa=[("Is h3 a mistake against the Fishing Pole?", "No. Kicking the knight is fine. The mistake is taking the knight after Black pushes the h-pawn."),
            ("Why is the free knight bad to take?", "Taking it opens the h-file next to your king. Black's queen and rook use that open line to give checkmate.")]),
    "petrov-trap": dict(
        title="Petrov Trap: why copying White loses your queen",
        desc="How the Petrov Trap works and how to avoid it, step by step on the board: why you kick the knight first before taking on e4.",
        guide=[
            dict(h="Don't copy right away", board=dict(moves="e4 e5 Nf3 Nf6 Nxe5", arrows=["g:d7d6"]), p=[
                "White takes your pawn. Taking White's pawn back with your knight looks fair, but it's risky.",
                "First kick White's knight with your d-pawn. Then take the pawn on e4."]),
            dict(h="If you copy: the queen comes to e2", board=dict(moves="e4 e5 Nf3 Nf6 Nxe5 Nxe4 Qe2", arrows=["r:e2e4"], rings=["!e8"]), p=[
                "The queen attacks your knight. Behind the knight stands your king."]),
            dict(h="Stay calm: block with your queen", board=dict(moves="e4 e5 Nf3 Nf6 Nxe5 Nxe4 Qe2", arrows=["g:d8e7"]), p=[
                "Put your queen on e7. White can take your knight, but after your d-pawn moves one square you win the knight on e5 back."]),
            dict(h="The blunder: the knight runs away", board=dict(moves="e4 e5 Nf3 Nf6 Nxe5 Nxe4 Qe2 Nf6 Nc6+", arrows=["r:e2e8", "r:c6d8"]), p=[
                "If your knight runs back, the line to your king opens. White's knight jumps to c6: check from the queen, and the knight attacks your queen. You lose the queen."]),
        ],
        qa=[("How do I avoid the Petrov Trap?", "After White takes your e5 pawn, play the d-pawn one square first. Take on e4 only after White's knight has moved back."),
            ("What if I already took on e4 and the queen comes to e2?", "Block with your queen on e7. Never move the knight away from the e-file.")]),
    "blackburne-shilling-gambit": dict(
        title="Blackburne Shilling Gambit: how to avoid the trap",
        desc="How to beat the Blackburne Shilling Gambit, step by step on the board: don't take the pawn, and what to do if you already did.",
        guide=[
            dict(h="A knight in the middle", board=dict(moves="e4 e5 Nf3 Nc6 Bc4 Nd4", arrows=["g:e1g1", "g:f3d4"]), p=[
                "Black's knight jumps to d4 and leaves the pawn on e5 unprotected. Don't take it.",
                "Castle, or take the knight on d4. Both keep you better."]),
            dict(h="If you take the pawn", board=dict(moves="e4 e5 Nf3 Nc6 Bc4 Nd4 Nxe5 Qg5", arrows=["r:g5e5", "r:g5g2"]), p=[
                "Black's queen comes to g5. It attacks your knight and the pawn in front of your rook."]),
            dict(h="Don't grab more: castle", board=dict(moves="e4 e5 Nf3 Nc6 Bc4 Nd4 Nxe5 Qg5", arrows=["g:e1g1"]), p=[
                "Castle. Your king now protects that pawn. The queen takes your knight, so you give the piece back, but your king is safe."]),
            dict(h="The greedy move", board=dict(moves="e4 e5 Nf3 Nc6 Bc4 Nd4 Nxe5 Qg5 Nxf7 Qxg2", arrows=["r:g2h1"]), p=[
                "If your knight takes another pawn on f7, the queen takes your pawn and attacks your rook."]),
            dict(h="How it ends", board=dict(moves="e4 e5 Nf3 Nc6 Bc4 Nd4 Nxe5 Qg5 Nxf7 Qxg2 Rf1 Qxe4+ Be2 Nf3#", rings=["!e1"]), p=[
                "The queen takes another pawn with check, your bishop blocks, and the knight jumps to f3. Checkmate."]),
        ],
        qa=[("Should I take the pawn on e5?", "No. Castle or take the knight on d4. The pawn is bait."),
            ("I took the pawn and the queen came to g5. What now?", "Castle right away and give the knight back. Don't take anything else.")]),
    "stafford-gambit": dict(
        title="Stafford Gambit: how to beat it and avoid the trap",
        desc="How to beat the Stafford Gambit, step by step on the board: which bishop move loses and which simple move keeps you a pawn up.",
        guide=[
            dict(h="Black gives a pawn", board=dict(moves="e4 e5 Nf3 Nf6 Nxe5 Nc6", arrows=["g:e5c6"]), p=[
                "Black leaves the pawn and brings out a knight. Taking that knight is fine: you stay a pawn up."]),
            dict(h="The bishop aims at f2", board=dict(moves="e4 e5 Nf3 Nf6 Nxe5 Nc6 Nxc6 dxc6 d3 Bc5", arrows=["r:c5f2"]), p=[
                "Black's bishop points at f2, the square next to your king. Black's pieces come out fast and look for tricks."]),
            dict(h="The fix: develop and castle", board=dict(moves="e4 e5 Nf3 Nf6 Nxe5 Nc6 Nxc6 dxc6 d3 Bc5", arrows=["g:f1e2"]), p=[
                "Bring your bishop to e2 and castle next. Simple moves keep your extra pawn and your king safe."]),
            dict(h="The mistake: pinning the knight", board=dict(moves="e4 e5 Nf3 Nf6 Nxe5 Nc6 Nxc6 dxc6 d3 Bc5 Bg5 Nxe4", arrows=["r:c5f2"]), p=[
                "Bishop to g5 attacks the queen, so it feels strong. But Black takes your pawn on e4 and lets you have the queen."]),
            dict(h="Take the queen and it's mate", board=dict(moves="e4 e5 Nf3 Nf6 Nxe5 Nc6 Nxc6 dxc6 d3 Bc5 Bg5 Nxe4 Bxd8 Bxf2+ Ke2 Bg4#", rings=["!e2"]), p=[
                "The bishop takes on f2 with check, your king must go to e2, and the other bishop comes to g4. Checkmate."]),
        ],
        qa=[("How do I beat the Stafford Gambit?", "Take the pawn, take the knight, then develop calmly: bishop to e2 and castle."),
            ("Why is taking the queen bad here?", "Because Black gets checkmate first. Before you grab a queen, look at every check your opponent has.")]),
    "halloween-gambit": dict(
        title="Halloween Gambit: how to beat it as Black",
        desc="How to beat the Halloween Gambit, step by step on the board: take the knight, find the one safe square, then strike back.",
        guide=[
            dict(h="A free knight", board=dict(moves="e4 e5 Nf3 Nc6 Nc3 Nf6 Nxe5", arrows=["g:c6e5"]), p=[
                "White gives a knight for your pawn. Take it. You are a whole piece up."]),
            dict(h="The pawns chase your knights", board=dict(moves="e4 e5 Nf3 Nc6 Nc3 Nf6 Nxe5 Nxe5 d4 Ng6 e5", arrows=["r:e5f6"]), p=[
                "White's pawns push forward and attack your knights. Now the knight on f6 is attacked."]),
            dict(h="Go back home", board=dict(moves="e4 e5 Nf3 Nc6 Nc3 Nf6 Nxe5 Nxe5 d4 Ng6 e5", arrows=["g:f6g8"]), p=[
                "Every square forward gets taken. Move the knight back to g8. It looks passive, but it is the only safe move."]),
            dict(h="Strike back in the center", board=dict(moves="e4 e5 Nf3 Nc6 Nc3 Nf6 Nxe5 Nxe5 d4 Ng6 e5 Ng8 Bc4", arrows=["r:c4f7", "g:d7d5"]), p=[
                "White's bishop aims at f7. Push your d-pawn two squares: it blocks the bishop and attacks it."]),
            dict(h="You come out ahead", board=dict(moves="e4 e5 Nf3 Nc6 Nc3 Nf6 Nxe5 Nxe5 d4 Ng6 e5 Ng8 Bc4 d5 Bxd5 N8e7"), p=[
                "White wins a pawn back, but your knight comes out and you are still a piece up. Now develop and castle."]),
        ],
        qa=[("Should I take the knight in the Halloween Gambit?", "Yes. Take it and then defend calmly. A whole extra piece wins in the end."),
            ("What is the key move to remember?", "When the pawn attacks your knight on f6, move the knight back to g8.")]),
    "elephant-trap": dict(
        title="Elephant Trap: why the free d5 pawn loses a piece",
        desc="How the Elephant Trap works in the Queen's Gambit, step by step on the board: why the pinned knight can still move and what to play instead.",
        guide=[
            dict(h="Your bishop pins the knight", board=dict(moves="d4 d5 c4 e6 Nc3 Nf6 Bg5 Nbd7", arrows=["y:g5d8"]), p=[
                "Your bishop stands in front of Black's knight on f6, with Black's queen behind it. It looks like that knight can't move."]),
            dict(h="The pawn looks free", board=dict(moves="d4 d5 c4 e6 Nc3 Nf6 Bg5 Nbd7 cxd5 exd5", rings=["!d5"]), p=[
                "After the pawn trade, the pawn on d5 seems to hang. Your knight could take it."]),
            dict(h="The fix: just develop", board=dict(moves="d4 d5 c4 e6 Nc3 Nf6 Bg5 Nbd7 cxd5 exd5", arrows=["g:e2e3"]), p=[
                "Play the e-pawn one square forward and keep developing. You keep a nice, safe position."]),
            dict(h="If you take: the surprise", board=dict(moves="d4 d5 c4 e6 Nc3 Nf6 Bg5 Nbd7 cxd5 exd5 Nxd5 Nxd5", arrows=["r:f8b4"]), p=[
                "Black takes back with the 'pinned' knight and leaves the queen for you. If you take it, the bishop comes to b4 with check."]),
            dict(h="Black wins a piece", board=dict(moves="d4 d5 c4 e6 Nc3 Nf6 Bg5 Nbd7 cxd5 exd5 Nxd5 Nxd5 Bxd8 Bb4+ Qd2 Bxd2+ Kxd2 Kxd8"), p=[
                "Your queen has to block the check, and Black takes it. The queens are gone and Black is a whole piece up."]),
        ],
        qa=[("Is the pinned knight really pinned?", "No. A pinned knight can still move if it wins something bigger. Here it wins your queen back with a check."),
            ("What should White play instead of taking on d5?", "Develop calmly with the e-pawn one square forward.")]),
    "lasker-trap": dict(
        title="Lasker Trap: the Albin Counter-Gambit trap and how to avoid it",
        desc="How the Lasker Trap works in the Albin Counter-Gambit, step by step on the board: the pawn that becomes a knight and the move to play instead.",
        guide=[
            dict(h="A pawn in your half of the board", board=dict(moves="d4 d5 c4 e5 dxe5 d4", arrows=["g:g1f3"]), p=[
                "Black gave a pawn and pushed the d-pawn into your half of the board. Bring your knight out to f3. That is the best move."]),
            dict(h="The mistake: attacking the pawn", board=dict(moves="d4 d5 c4 e5 dxe5 d4 e3 Bb4+ Bd2 dxe3", arrows=["r:e3f2", "g:f2e3"]), p=[
                "After the e-pawn move and a check, Black takes on e3. Now the pawn threatens your f-pawn, right next to your king.",
                "Take that pawn with your f-pawn. Don't take the bishop."]),
            dict(h="Take the bishop and it falls apart", board=dict(moves="d4 d5 c4 e5 dxe5 d4 e3 Bb4+ Bd2 dxe3 Bxb4 exf2+ Ke2 fxg1=N+", rings=["!e2"]), p=[
                "The pawn takes on f2 with check and then becomes a knight on g1, again with check. A knight, not a queen, because the check gives you no time.",
                "Black is winning material and your king is stuck in the middle."]),
        ],
        qa=[("How do I avoid the Lasker Trap?", "Bring your knight to f3 instead of pushing the e-pawn."),
            ("Why does Black promote to a knight?", "Because the knight gives check. White has no time to fight back, and Black wins more material.")]),
    "siberian-trap": dict(
        title="Siberian Trap: the Smith-Morra trap and how to avoid it",
        desc="How the Siberian Trap works in the Smith-Morra Gambit, step by step on the board: two pieces aim at h2, and the move that keeps you safe.",
        guide=[
            dict(h="Two pieces aim at h2", board=dict(moves="e4 c5 d4 cxd4 c3 dxc3 Nxc3 Nc6 Nf3 e6 Bc4 Qc7 O-O Nf6 Qe2 Ng4", arrows=["r:c7h2", "r:g4h2"]), p=[
                "Black's queen and knight both aim at h2, next to your king. Your knight on f3 is the piece that keeps them out."]),
            dict(h="The fix: chase the queen", board=dict(moves="e4 c5 d4 cxd4 c3 dxc3 Nxc3 Nc6 Nf3 e6 Bc4 Qc7 O-O Nf6 Qe2 Ng4", arrows=["g:c3b5"]), p=[
                "Jump with your other knight to b5 and attack the queen. Moving your rook to d1 is also good. What matters: don't kick the knight on g4."]),
            dict(h="The mistake: kicking the knight", board=dict(moves="e4 c5 d4 cxd4 c3 dxc3 Nxc3 Nc6 Nf3 e6 Bc4 Qc7 O-O Nf6 Qe2 Ng4 h3 Nd4", arrows=["r:d4e2", "r:c7h2"]), p=[
                "If you kick the knight with the h-pawn, Black's other knight jumps to d4 and attacks your queen."]),
            dict(h="How it ends", board=dict(moves="e4 c5 d4 cxd4 c3 dxc3 Nxc3 Nc6 Nf3 e6 Bc4 Qc7 O-O Nf6 Qe2 Ng4 h3 Nd4 Nxd4 Qh2#", rings=["!g1"]), p=[
                "If your knight takes on d4, nothing defends h2 anymore. The queen goes there: checkmate."]),
        ],
        qa=[("How do I avoid the Siberian Trap?", "When the queen and knight both aim at h2, don't kick the knight with the h-pawn. Attack the queen with your knight on b5 or bring a rook to d1 instead."),
            ("What is the lesson?", "When two enemy pieces aim at the square next to your king, keep the defender of that square where it is.")]),
}
for _t in TRAPS:
    if _t["slug"] in GUIDES: _t.update(GUIDES[_t["slug"]])
