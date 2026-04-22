"""
RAG Retriever - Retrieval-Augmented Generation module for
fetching relevant product documentation based on user queries.
"""

import os
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class RAGRetriever:
    """
    Retrieves relevant product documentation using vector similarity search.
    
    Uses FAISS + OpenAI embeddings when available, falls back to 
    keyword-based retrieval for simpler deployments.
    """
    
    def __init__(self, docs_path: str = None):
        self.docs_path = docs_path or os.path.join(
            os.path.dirname(__file__), "..", "data", "product_docs.json"
        )
        self.documents = []
        self.vectorstore = None
        self._load_documents()
        self._init_vectorstore()
    
    def _load_documents(self):
        """Load product documentation from JSON file."""
        try:
            docs_file = Path(self.docs_path)
            if docs_file.exists():
                with open(docs_file, "r") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                logger.info(f"Loaded {len(self.documents)} product documents")
            else:
                logger.warning(f"Product docs not found at {self.docs_path}. Using built-in docs.")
                self.documents = self._get_builtin_docs()
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            self.documents = self._get_builtin_docs()
    
    def _init_vectorstore(self):
        """Initialize FAISS vectorstore with OpenAI embeddings."""
        try:
            from langchain_openai import OpenAIEmbeddings
            from langchain_community.vectorstores import FAISS
            from langchain.schema import Document
            
            if not os.getenv("OPENAI_API_KEY"):
                logger.warning("No OpenAI API key, using keyword search")
                return
            
            embeddings = OpenAIEmbeddings(
                model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            )
            
            # Convert documents to LangChain Document objects
            lc_docs = [
                Document(
                    page_content=doc["content"],
                    metadata={"title": doc.get("title", ""), "category": doc.get("category", "")}
                )
                for doc in self.documents
            ]
            
            self.vectorstore = FAISS.from_documents(lc_docs, embeddings)
            logger.info("FAISS vectorstore initialized successfully")
            
        except ImportError:
            logger.warning("LangChain/FAISS not available. Using keyword search fallback.")
        except Exception as e:
            logger.warning(f"Vectorstore init failed: {e}. Using keyword search fallback.")
    
    def retrieve(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User's question or message
            top_k: Number of documents to retrieve
            
        Returns:
            Concatenated relevant document excerpts
        """
        try:
            if self.vectorstore:
                return self._vector_retrieve(query, top_k)
            else:
                return self._keyword_retrieve(query, top_k)
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return self._keyword_retrieve(query, top_k)
    
    def _vector_retrieve(self, query: str, top_k: int) -> str:
        """Use FAISS for semantic similarity retrieval."""
        docs = self.vectorstore.similarity_search(query, k=top_k)
        
        if not docs:
            return ""
        
        context_parts = []
        for doc in docs:
            title = doc.metadata.get("title", "")
            content = doc.page_content
            if title:
                context_parts.append(f"### {title}\n{content}")
            else:
                context_parts.append(content)
        
        return "\n\n".join(context_parts)
    
    def _keyword_retrieve(self, query: str, top_k: int) -> str:
        """Keyword-based fallback retrieval."""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_docs = []
        for doc in self.documents:
            content_lower = doc["content"].lower()
            title_lower = doc.get("title", "").lower()
            
            # Score based on keyword overlap
            score = sum(1 for word in query_words if word in content_lower or word in title_lower)
            
            # Boost for category matches
            category = doc.get("category", "").lower()
            if any(word in category for word in query_words):
                score += 2
            
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and take top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = [doc for _, doc in scored_docs[:top_k]]
        
        if not top_docs:
            # Return general overview if no matches
            return self.documents[0]["content"] if self.documents else ""
        
        context_parts = []
        for doc in top_docs:
            title = doc.get("title", "")
            content = doc["content"]
            if title:
                context_parts.append(f"### {title}\n{content}")
            else:
                context_parts.append(content)
        
        return "\n\n".join(context_parts)
    
    def _get_builtin_docs(self) -> List[Dict]:
        """Built-in product documentation as fallback."""
        return [
            {
                "title": "Inflix Overview",
                "category": "overview",
                "content": """Inflix is an AI-powered social media automation platform designed for businesses, 
agencies, and creators. It combines intelligent scheduling, AI content generation, 
and deep analytics to help you grow your social media presence efficiently.

Key capabilities:
- AI-powered content generation (captions, hashtags, images)
- Smart scheduling with optimal timing recommendations  
- Multi-platform support: Instagram, Twitter/X, LinkedIn, Facebook, TikTok
- Detailed analytics and performance tracking
- Team collaboration features
- Competitor monitoring and benchmarking"""
            },
            {
                "title": "Pricing Plans",
                "category": "pricing",
                "content": """Inflix offers three pricing tiers:

**Starter Plan - $29/month**
- Up to 5 social accounts
- 30 scheduled posts per month
- Basic analytics
- AI caption generation (50 credits/mo)
- Email support

**Growth Plan - $79/month**  
- Up to 15 social accounts
- Unlimited scheduled posts
- Advanced analytics + competitor tracking
- AI content generation (500 credits/mo)
- Priority email & chat support
- Team members (up to 3)

**Enterprise Plan - Custom pricing**
- Unlimited accounts
- Custom AI model fine-tuning
- Dedicated account manager
- SSO & advanced security
- API access
- SLA guarantees

All plans include a **14-day free trial** with no credit card required."""
            },
            {
                "title": "AI Features",
                "category": "features",
                "content": """Inflix AI Features:

**AI Caption Generator**: Generates platform-optimized captions based on your brand voice, 
image content, and target audience. Supports 20+ languages.

**Smart Hashtag Suggester**: Analyzes trending hashtags and your niche to suggest the 
most effective hashtag sets for each post.

**Optimal Timing AI**: Learns your audience's activity patterns and recommends the best 
posting times to maximize reach and engagement.

**Content Ideation**: Provides weekly content ideas tailored to your industry and audience 
based on trending topics and competitor analysis.

**Auto-Responder**: AI-powered comment and DM responses to increase engagement."""
            },
            {
                "title": "Integrations",
                "category": "integrations",
                "content": """Inflix integrates with:

**Social Platforms**: Instagram, Twitter/X, LinkedIn, Facebook Pages & Groups, TikTok, 
Pinterest, YouTube

**Tools & Apps**:
- Canva (design assets)
- Google Drive & Dropbox (media storage)
- Slack (notifications)
- Zapier (workflow automation)
- HubSpot & Salesforce (CRM sync)
- Shopify (e-commerce posting)
- Google Analytics (traffic tracking)

**API**: Full REST API available on Growth and Enterprise plans."""
            },
            {
                "title": "Getting Started",
                "category": "onboarding",
                "content": """Getting started with Inflix is simple:

1. **Sign up** at inflix.ai (no credit card required for trial)
2. **Connect your accounts**: Link your social media profiles in under 2 minutes
3. **Set up your brand voice**: Tell Inflix about your brand tone and audience
4. **Create your first post**: Use AI to generate content or upload your own
5. **Schedule**: Pick your posting schedule or let AI optimize it for you

The onboarding takes about 10 minutes and our team is available 24/7 to help."""
            }
        ]
