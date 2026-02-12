import logging
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph
from typing import Any, Dict, AsyncIterator

from logger.universal_logger import setup_logger
from schema.state import InputState
from nodes.grounding import GroundingNode
from nodes.editor import EditorNode
from nodes.collector import CollectorNode
from nodes.research_nodes.customers import CustomersResearcher
from nodes.research_nodes.triggers import TriggersResearcher
from nodes.research_nodes.news import NewsResearcher
from nodes.research_nodes.offerings import OfferingsResearcher
from nodes.research_nodes.readiness import ReadinessResearcher

logger = logging.getLogger(__name__)

class Graph:
    def __init__(self, company="Unknown", url="Unknown", hq_location="Unknown", industry="Unknown") -> None:
        self.input_state = InputState(
            company=company,
            company_url=url,
            hq_location=hq_location,
            industry=industry
        )
        self._init_nodes()
        self._build_workflow()
    
    def _init_nodes(self):
        self.ground = GroundingNode()
        self.news_analyst = NewsResearcher()
        self.customer_researcher = CustomersResearcher()
        self.offering_researcher = OfferingsResearcher()
        self.readiness_researcher = ReadinessResearcher()
        self.triggers_researcher = TriggersResearcher()
        self.collector = CollectorNode()
        self.editor = EditorNode()

    def _build_workflow(self):
        self.workflow = StateGraph(InputState)

        self.workflow.add_node("grounding", self.ground.run)
        self.workflow.add_node("triggers_researcher", self.triggers_researcher.run)
        self.workflow.add_node("offering_researcher", self.offering_researcher.run)
        self.workflow.add_node("readiness_researcher", self.readiness_researcher.run)
        self.workflow.add_node("customer_researcher", self.customer_researcher.run)
        self.workflow.add_node("news_analyst", self.news_analyst.run)
        self.workflow.add_node("collector", self.collector.run)
        self.workflow.add_node("editor", self.editor.run)

        self.workflow.set_entry_point("grounding")
        self.workflow.set_finish_point("editor")

        self.workflow.add_edge("grounding", "triggers_researcher")
        self.workflow.add_edge("grounding", "readiness_researcher")
        self.workflow.add_edge("grounding", "offering_researcher")
        self.workflow.add_edge("grounding", "customer_researcher")
        self.workflow.add_edge("grounding", "news_analyst")

        self.workflow.add_edge("triggers_researcher", "collector")
        self.workflow.add_edge("readiness_researcher", "collector")
        self.workflow.add_edge("offering_researcher", "collector")
        self.workflow.add_edge("customer_researcher", "collector")
        self.workflow.add_edge("news_analyst", "collector")

        self.workflow.add_edge("collector", "editor")

    async def run(self, thread: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Execute the research workflow"""
        compiled_graph = self.workflow.compile()
        
        async for state in compiled_graph.astream(
            self.input_state,
            thread
        ):
            yield state
    
    def compile(self):
        graph = self.workflow.compile()
        return graph