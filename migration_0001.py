from sqlalchemy import create_engine, select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from models import Base, Migration


def run_migration():
    engine = create_engine('postgresql://ketchuser:secureketchpassword789@db:5432/takehome')

    # check if migration has run already
    with Session(engine) as session:
        try:
            migration_select_stmt = select(Migration).where(Migration.name=="migration_0001")
            migration_result = session.execute(migration_select_stmt)
            migration_0001 = migration_result.scalars().all()[0]
            if migration_0001.migrated is True:
                print('Migration has already ran, skipping')
                return True
        except ProgrammingError:
            print('Not able to find migration table, will run migration_0001')

    Base.metadata.create_all(engine)

    # mark migration as migrated
    with Session(engine) as session:
        migration_0001 = Migration(
            name="migration_0001",
            migrated=True,
        )
        session.add_all([migration_0001])
        session.commit()
    
    return True