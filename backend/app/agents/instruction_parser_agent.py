from app.schemas.instructions import LongInstructionInput, ParsedInstructionSpec
from app.utils.instruction_utils import parse_instruction_rule_based


class InstructionParserAgent:
    def run(self, payload: LongInstructionInput) -> ParsedInstructionSpec:
        return parse_instruction_rule_based(payload.raw_text, payload.language_hint)
