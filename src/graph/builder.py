from langgraph.constants import START
from langgraph.graph import StateGraph

from src.graph.nodes.postNodes.analyze import analyze
from src.graph.nodes.postNodes.reddit_data import reddit_data
from src.graph.nodes.postNodes.extract import extract_keywords
from src.graph.nodes.wordCloudNodes.word_seg import word_seg
from src.graph.state import State, WordCloudState


def build_graph():
    builder = StateGraph(State)
    builder.add_edge(START, "extract_keywords")
    builder.add_node("extract_keywords", extract_keywords)
    builder.add_node("reddit_data", reddit_data)
    builder.add_node("analyze", analyze)

    return builder.compile()


def build_word_cloud_graph():
    builder = StateGraph(WordCloudState)
    builder.add_edge(START, "word_seg")
    builder.add_node("word_seg", word_seg)
    return builder.compile()