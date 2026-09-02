from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.search import StructuredSearchQuery, NaturalLanguageQuery, NLQueryResult, SearchSummaryResponse
from backend.services.search_service import search_service

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.post("/structured", response_model=SearchSummaryResponse)
def search_structured(query: StructuredSearchQuery, db: Session = Depends(get_db)):
    return search_service.search_structured(query, db)

@router.post("/nlp", response_model=NLQueryResult)
def search_natural_language(nl_query: NaturalLanguageQuery, db: Session = Depends(get_db)):
    return search_service.execute_natural_language_query(nl_query.query, db)
