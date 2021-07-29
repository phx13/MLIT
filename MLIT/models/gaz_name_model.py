from sqlalchemy import MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

from MLIT import db


class GazNameModel(db.Model):
    __tablename__ = 'gaz_names'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)

    """
    name: varchar
    """

    @staticmethod
    def search_all_gaz_name():
        try:
            return db.session.query(GazNameModel).all()
        except SQLAlchemyError:
            return 'server error'

    @staticmethod
    def search_all_locs():
        try:
            return db.session.query(GazNameModel.name).distinct().all()
        except SQLAlchemyError:
            return 'server error'

    @staticmethod
    def search_all_gpes():
        try:
            return db.session.query(GazNameModel.land_district).distinct().all()
        except SQLAlchemyError:
            return 'server error'
