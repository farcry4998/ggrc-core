# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Drop gdrive integration service table

Create Date: 2018-01-17 09:50:52.621554
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = '40d92baab48c'
down_revision = '19a260ec358e'


def upgrade():
  """Drop alembic table for gdrive migrations.

  For db_reset, this table isn't supposed to exist since the migration
  chain is disabled.

  For existing databases, this table exists but won't be used since
  the migration chain is disabled.
  """
  op.execute("""
      DROP TABLE IF EXISTS ggrc_gdrive_integration_alembic_version
  """)

  # The following duplicates a part of a gdrive-related migration,
  # since a bunch of old migrations in ggrc refer to meetings table.
  # This part is relevant only for db_reset (new databases), so we
  # shouldn't recreate this table in downgrade.
  op.execute("""
      DROP TABLE IF EXISTS meetings
  """)


def downgrade():
  """Restore alembic table for gdrive migrations with latest correct content.

  Since the migration chain is disabled, this table won't be used. If
  the migration chain gets enabled, this table will contain correct
  tag for downgrades.
  """
  op.execute("""
      CREATE TABLE ggrc_gdrive_integration_alembic_version (
          version_num varchar(32) NOT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8
  """)
  op.execute("""
      INSERT INTO ggrc_gdrive_integration_alembic_version (version_num)
      VALUES ('3f64d03c6c01')
  """)
