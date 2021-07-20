from sqlalchemy import MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

from MLIT import db


class TrainDataModel(db.Model):
    __tablename__ = 'train_data'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)

    """
    text: text
    entities: varchar {'entities': entities}
    """

    @staticmethod
    def add_train_data(text, entities):
        try:
            db.session.add(TrainDataModel(text=text, entities=entities))
            db.session.commit()
        except SQLAlchemyError:
            return 'server error'
