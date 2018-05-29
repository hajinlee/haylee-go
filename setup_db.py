#!/usr/bin/env python

from sqlalchemy import create_engine
import schema
import os

db_engine = create_engine(os.environ['HAYLEE_DB'], echo=True, client_encoding='utf8')

conn = db_engine.connect()

schema.metadata.create_all(db_engine)
