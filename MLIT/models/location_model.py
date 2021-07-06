from sqlalchemy import MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

from MLIT import db


class LocationModel(db.Model):
    __tablename__ = 'location'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)

    """
    id: int, primary key, auto_increment
    context: text
    """

    @staticmethod
    def search_first_context():
        try:
            return db.session.query(LocationModel).first()
        except SQLAlchemyError:
            return 'server error'
