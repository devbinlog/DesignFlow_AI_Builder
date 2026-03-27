from uuid import UUID


class DesignFlowException(Exception):
    """기본 예외 클래스"""
    pass


class ProjectNotFoundException(DesignFlowException):
    def __init__(self, project_id: UUID | str):
        self.project_id = project_id
        super().__init__(f"프로젝트를 찾을 수 없습니다: {project_id}")


class AnalysisNotFoundException(DesignFlowException):
    def __init__(self, analysis_id: UUID | str):
        self.analysis_id = analysis_id
        super().__init__(f"분석을 찾을 수 없습니다: {analysis_id}")


class InvalidFigmaJsonException(DesignFlowException):
    def __init__(self, detail: str = "유효하지 않은 Figma JSON 형식입니다"):
        super().__init__(detail)


class AIServiceException(DesignFlowException):
    def __init__(self, detail: str = "AI 서비스 호출에 실패했습니다"):
        super().__init__(detail)
