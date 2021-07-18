from sqlalchemy import MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

from MLIT import db


class LocalityModel(db.Model):
    __tablename__ = 'locality_data'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)

    """
    site_id: int, primary key, auto_increment
    East: int
    North: int
    Locality: text
    """

    @staticmethod
    def search_all_locality():
        try:
            return db.session.query(LocalityModel).distinct(LocalityModel.Locality).all()
        except SQLAlchemyError:
            return 'server error'
