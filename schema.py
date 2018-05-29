from sqlalchemy import MetaData, Table, Column, Index, Integer, BigInteger, Boolean, String, ForeignKey, UniqueConstraint

# we use 64-character UUIDs for some things
UUID_LENGTH = 64

uuid_type = String(UUID_LENGTH)

metadata = MetaData()

Users = Table('users', metadata,
              Column('user_id', uuid_type, unique = True, primary_key = True),

              # note: Facebook-based accounts may not include an email address
              Column('email', String(64), nullable = True, unique = True),
              Column('name', String(64), nullable = True),
              #Column('last_name', String(64), nullable = True),
              Column('email_verified', Boolean, nullable = False),

              Column('creation_time', BigInteger(), nullable = False),
              Column('last_login_time', BigInteger(), nullable = False),

              Column('rating', Integer(), nullable = False),
              Column('aga_number', Integer(), nullable = True),
              Column('egf_number', Integer(), nullable = True),

              # true = opted in, false = opted out, NULL = did not respond yet
              Column('email_notifications_enabled', Boolean, nullable = True),
              Column('facebook_notifications_enabled', Boolean, nullable = True),
              )

Games = Table('games', metadata,
              Column('game_id', uuid_type, unique = True, primary_key = True),

              # note: these are foreign keys into the users table, but we want the ability to delete
              # a user without deleting their old games, so we don't use a foreign key constraint.
              Column('black_id', uuid_type, index = True, nullable = False),
              Column('white_id', uuid_type, index = True, nullable = False),

              # board size (9, 13, or 19)
              Column('size', Integer(), nullable = False),

              Column('rules', Integer(), nullable = False),
              # 0: AGA rules
              # 1: Japanese rules
              # 2: Chinese rules
              # 3: Ing rules
              # 4: Korean rules

              Column('time_setting', String(25), nullable = False),
              # (will be parsed by separate code)
              # '10m 3x30s'
              # '3d per move'

              Column('start_time', BigInteger(), nullable = False),
              Column('last_move_time', BigInteger(), nullable = True),

              Column('last_move_player', Integer(), nullable = True),
              # NULL: no moves played yet
              # 0: Black
              # 1: White

              Column('moves', String(), nullable = False, default = ''),
              Column('status', Integer(), nullable = False),
              # 0: Playing
              # 1: Over
              # 2: Scoring
              )

Scores = Table('scores', metadata,
               Column('user_id', uuid_type, index = True),
               Column('score', Integer(), nullable = False, default = 0),
               Column('season', Integer(), nullable = False),
               # 0 = 2018 summer
               Index('ix_user_id_and_season', 'user_id', 'season', unique = True),
               Index('ix_season_scores', 'season', 'score'),
               )
