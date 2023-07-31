"""CRUD tests for WalletDelta"""
import numpy as np
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from elfpy.data import postgres
from elfpy.data.db_schema import Base, WalletDelta

engine = create_engine("sqlite:///:memory:")  # in-memory SQLite database for testing
Session = sessionmaker(bind=engine)

# fixture arguments in test function have to be the same as the fixture name
# pylint: disable=redefined-outer-name


@pytest.fixture(scope="function")
def session():
    """Session fixture for tests"""
    Base.metadata.create_all(engine)  # create tables
    session_ = Session()
    yield session_
    session_.close()
    Base.metadata.drop_all(engine)  # drop tables


class TestWalletDeltaTable:
    """CRUD tests for WalletDelta table"""

    def test_create_wallet_delta(self, session):
        """Create and entry"""
        # Note: this test is using inmemory sqlite, which doesn't seem to support
        # autoincrementing ids without init, whereas postgres does this with no issues
        # Hence, we explicitly add id here
        wallet_delta = WalletDelta(blockNumber=1, tokenDelta=3.2)  # add your other columns here...
        session.add(wallet_delta)
        session.commit()

        retrieved_wallet_delta = session.query(WalletDelta).filter_by(blockNumber=1).first()
        assert retrieved_wallet_delta is not None
        # toekValue retreieved from postgres is in Decimal, cast to float
        assert float(retrieved_wallet_delta.tokenDelta) == 3.2

    def test_update_wallet_delta(self, session):
        """Update an entry"""
        wallet_delta = WalletDelta(blockNumber=1, tokenDelta=3.2)
        session.add(wallet_delta)
        session.commit()

        wallet_delta.tokenDelta = 5.0
        session.commit()

        updated_wallet_delta = session.query(WalletDelta).filter_by(blockNumber=1).first()
        # tokenDelta retreieved from postgres is in Decimal, cast to float
        assert float(updated_wallet_delta.tokenDelta) == 5.0

    def test_delete_wallet_delta(self, session):
        """Delete an entry"""
        wallet_delta = WalletDelta(blockNumber=1, tokenDelta=3.2)
        session.add(wallet_delta)
        session.commit()

        session.delete(wallet_delta)
        session.commit()

        deleted_wallet_delta = session.query(WalletDelta).filter_by(blockNumber=1).first()
        assert deleted_wallet_delta is None


class TestWalletDeltaInterface:
    """Testing postgres interface for walletinfo table"""

    def test_latest_block_number(self, session):
        """Testing retrevial of wallet info via interface"""
        wallet_delta_1 = WalletDelta(blockNumber=1, tokenDelta=3.0)  # add your other columns here...
        postgres.add_wallet_deltas([wallet_delta_1], session)

        latest_block_number = postgres.get_latest_block_number_from_table(WalletDelta, session)
        assert latest_block_number == 1

        wallet_delta_2 = WalletDelta(blockNumber=2, tokenDelta=3.2)  # add your other columns here...
        wallet_delta_3 = WalletDelta(blockNumber=3, tokenDelta=3.4)  # add your other columns here...
        postgres.add_wallet_deltas([wallet_delta_2, wallet_delta_3], session)

        latest_block_number = postgres.get_latest_block_number_from_table(WalletDelta, session)
        assert latest_block_number == 3

    def test_get_wallet_delta(self, session):
        """Testing retrevial of walletinfo via interface"""
        wallet_delta_1 = WalletDelta(blockNumber=0, tokenDelta=3.1)  # add your other columns here...
        wallet_delta_2 = WalletDelta(blockNumber=1, tokenDelta=3.2)  # add your other columns here...
        wallet_delta_3 = WalletDelta(blockNumber=2, tokenDelta=3.3)  # add your other columns here...
        postgres.add_wallet_deltas([wallet_delta_1, wallet_delta_2, wallet_delta_3], session)

        wallet_delta_df = postgres.get_wallet_deltas(session)
        np.testing.assert_array_equal(wallet_delta_df["tokenDelta"], np.array([3.1, 3.2, 3.3]))

    def test_block_query_wallet_delta(self, session):
        """Testing querying by block number of wallet info via interface"""
        wallet_delta_1 = WalletDelta(blockNumber=0, tokenDelta=3.1)  # add your other columns here...
        wallet_delta_2 = WalletDelta(blockNumber=1, tokenDelta=3.2)  # add your other columns here...
        wallet_delta_3 = WalletDelta(blockNumber=2, tokenDelta=3.3)  # add your other columns here...
        postgres.add_wallet_deltas([wallet_delta_1, wallet_delta_2, wallet_delta_3], session)

        wallet_delta_df = postgres.get_wallet_deltas(session, start_block=1)
        np.testing.assert_array_equal(wallet_delta_df["tokenDelta"], np.array([3.2, 3.3]))

        wallet_delta_df = postgres.get_wallet_deltas(session, start_block=-1)
        np.testing.assert_array_equal(wallet_delta_df["tokenDelta"], np.array([3.3]))

        wallet_delta_df = postgres.get_wallet_deltas(session, end_block=1)
        np.testing.assert_array_equal(wallet_delta_df["tokenDelta"], np.array([3.1]))

        wallet_delta_df = postgres.get_wallet_deltas(session, end_block=-1)
        np.testing.assert_array_equal(wallet_delta_df["tokenDelta"], np.array([3.1, 3.2]))

        wallet_delta_df = postgres.get_wallet_deltas(session, start_block=1, end_block=-1)
        np.testing.assert_array_equal(wallet_delta_df["tokenDelta"], np.array([3.2]))
