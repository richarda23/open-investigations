from uuid import UUID

from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Optional

from langchain.schema import BaseMessage, AgentFinish, AgentAction, LLMResult


class MyStreamLitHandler(BaseCallbackHandler):
    """
        A callback handler that logs Langchain events to a Streamlit container.
    """

    def __init__(self, container):
        self.container = container

    def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], *, run_id: UUID,
                            parent_run_id: Optional[UUID] = None, tags: Optional[List[str]] = None,
                            metadata: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        pass

    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        class_name = serialized.get("name", serialized.get("id", ["<unknown>"])[-1])
        docs = inputs.get('input_documents', [])
        names = ','.join([d.metadata['source'] for d in docs])
        self.container.write(f"\n\n:sunglasses: Entering new chain... {class_name} , analysing {names} :sunglasses:")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        self.container.write(":sunglasses: Finished chain.:sunglasses:")

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        self.container.write(f"chain error {error}: , {kwargs}")

    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Print out the prompts."""
        self.container.write(f"LLM  starting..")
        for p in prompts:
            abbrev = p
            if len(abbrev > 500):
                abbrev = f"{p[:500]}..."
            self.container.write(abbrev)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.container.write(f"LLM  ending..")

    def on_text(
            self,
            text: str,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            **kwargs: Any,
    ) -> Any:
        abbreviated = text
        if len(text) > 200:
            abbreviated = text[0:200]
        self.container.write(f"Received text - {abbreviated}.....")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Do nothing."""
        pass

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        """Do nothing."""
        pass

    def on_tool_start(
            self,
            serialized: Dict[str, Any],
            input_str: str,
            **kwargs: Any,
    ) -> None:
        """Do nothing."""
        pass

    def on_agent_action(
            self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """Run on agent action."""
        pass

    def on_tool_end(
            self,
            output: str,
            color: Optional[str] = None,
            observation_prefix: Optional[str] = None,
            llm_prefix: Optional[str] = None,
            **kwargs: Any,
    ) -> None:
        pass

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        """Do nothing."""
        pass

    def on_agent_finish(
            self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Run on agent end."""
        pass
