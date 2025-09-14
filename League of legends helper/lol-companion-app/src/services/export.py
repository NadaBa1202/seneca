"""
Data export and replay functionality for League of Legends Companion App.

This module provides comprehensive data export capabilities including match data,
analytics, highlights, and replay functionality for analysis and sharing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, BinaryIO
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import csv
import pandas as pd
import io
import zipfile
from pathlib import Path
import base64

from ..config import get_config
from ..models import (
    HistoricalMatch, LiveMatch, Participant, Team, MatchEvent,
    MatchSummary, PlayerAnalytics, TeamAnalytics, MatchAnalytics
)
from ..services.analytics import get_match_analyzer
from ..services.event_detection import get_event_service
from ..services.chatbot import get_chatbot
from ..nlp import get_nlp_pipeline

logger = logging.getLogger(__name__)
config = get_config()


class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"


class ExportType(Enum):
    """Types of data to export."""
    MATCH_DATA = "match_data"
    ANALYTICS = "analytics"
    HIGHLIGHTS = "highlights"
    PLAYER_STATS = "player_stats"
    TEAM_STATS = "team_stats"
    EVENT_TIMELINE = "event_timeline"
    CHAT_LOG = "chat_log"
    COMPREHENSIVE = "comprehensive"


@dataclass
class ExportOptions:
    """Options for data export."""
    format: ExportFormat
    export_type: ExportType
    include_timeline: bool = True
    include_analytics: bool = True
    include_highlights: bool = True
    include_chat_log: bool = False
    include_images: bool = False
    compress: bool = False
    custom_fields: List[str] = None
    
    def __post_init__(self):
        if self.custom_fields is None:
            self.custom_fields = []


@dataclass
class ExportResult:
    """Result of an export operation."""
    success: bool
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MatchDataExporter:
    """Exports match data in various formats."""
    
    def __init__(self):
        self.match_analyzer = None
        self.event_service = None
        self.nlp_pipeline = None
    
    async def initialize(self):
        """Initialize the exporter."""
        self.match_analyzer = await get_match_analyzer()
        self.event_service = await get_event_service()
        self.nlp_pipeline = await get_nlp_pipeline()
        logger.info("Match Data Exporter initialized")
    
    async def export_match(
        self, 
        match: Union[HistoricalMatch, LiveMatch], 
        options: ExportOptions,
        output_path: Optional[str] = None
    ) -> ExportResult:
        """
        Export match data in the specified format.
        
        Args:
            match: Match data to export
            options: Export configuration
            output_path: Optional custom output path
            
        Returns:
            ExportResult with export information
        """
        try:
            # Generate output path if not provided
            if not output_path:
                output_path = self._generate_output_path(match, options)
            
            # Prepare data based on export type
            export_data = await self._prepare_export_data(match, options)
            
            # Export in specified format
            if options.format == ExportFormat.JSON:
                result = await self._export_json(export_data, output_path, options)
            elif options.format == ExportFormat.CSV:
                result = await self._export_csv(export_data, output_path, options)
            elif options.format == ExportFormat.EXCEL:
                result = await self._export_excel(export_data, output_path, options)
            elif options.format == ExportFormat.HTML:
                result = await self._export_html(export_data, output_path, options)
            elif options.format == ExportFormat.MARKDOWN:
                result = await self._export_markdown(export_data, output_path, options)
            else:
                return ExportResult(
                    success=False,
                    error_message=f"Unsupported export format: {options.format.value}"
                )
            
            # Compress if requested
            if options.compress and result.success:
                result = await self._compress_export(result, options)
            
            return result
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return ExportResult(
                success=False,
                error_message=str(e)
            )
    
    async def _prepare_export_data(self, match: Union[HistoricalMatch, LiveMatch], options: ExportOptions) -> Dict[str, Any]:
        """Prepare data for export based on options."""
        export_data = {
            "match_info": {
                "match_id": getattr(match, 'match_id', getattr(match, 'game_id', 'unknown')),
                "game_mode": match.game_mode.value,
                "duration": getattr(match, 'game_duration', getattr(match, 'game_length', 0)),
                "creation_time": getattr(match, 'game_creation', getattr(match, 'game_start_time', datetime.now())),
                "map_id": getattr(match, 'map_id', 11)
            },
            "participants": [self._serialize_participant(p) for p in match.participants],
            "teams": [self._serialize_team(t) for t in match.teams]
        }
        
        # Add timeline if requested
        if options.include_timeline and hasattr(match, 'timeline'):
            export_data["timeline"] = [self._serialize_event(e) for e in match.timeline]
        
        # Add analytics if requested
        if options.include_analytics:
            analytics = await self.match_analyzer.analyze_match(match)
            export_data["analytics"] = self._serialize_analytics(analytics)
        
        # Add highlights if requested
        if options.include_highlights and hasattr(match, 'timeline'):
            highlights = await self.event_service.generate_match_summary(match.timeline, match.participants)
            export_data["highlights"] = highlights.get("highlights", [])
        
        # Add chat log if requested
        if options.include_chat_log:
            chatbot = await get_chatbot()
            chat_history = chatbot.get_conversation_history()
            export_data["chat_log"] = chat_history
        
        return export_data
    
    def _serialize_participant(self, participant: Participant) -> Dict[str, Any]:
        """Serialize participant data for export."""
        return {
            "summoner_name": participant.summoner_name,
            "champion_id": participant.champion_id,
            "champion_name": participant.champion_name,
            "team_id": participant.team_id,
            "role": participant.role,
            "lane": participant.lane,
            "stats": {
                "kills": participant.stats.kills,
                "deaths": participant.stats.deaths,
                "assists": participant.stats.assists,
                "gold_earned": participant.stats.gold_earned,
                "total_damage_dealt": participant.stats.total_damage_dealt,
                "total_damage_taken": participant.stats.total_damage_taken,
                "vision_score": participant.stats.vision_score,
                "cs": participant.stats.cs,
                "level": participant.stats.level
            }
        }
    
    def _serialize_team(self, team: Team) -> Dict[str, Any]:
        """Serialize team data for export."""
        return {
            "team_id": team.team_id,
            "win": team.win,
            "bans": team.bans,
            "objectives": team.objectives,
            "participant_count": len(team.participants)
        }
    
    def _serialize_event(self, event: MatchEvent) -> Dict[str, Any]:
        """Serialize match event for export."""
        return {
            "event_type": event.event_type.value,
            "timestamp": event.timestamp,
            "participant_id": event.participant_id,
            "killer_id": event.killer_id,
            "victim_id": event.victim_id,
            "assisting_participant_ids": event.assisting_participant_ids,
            "position": event.position,
            "metadata": event.metadata
        }
    
    def _serialize_analytics(self, analytics: MatchAnalytics) -> Dict[str, Any]:
        """Serialize analytics data for export."""
        return {
            "match_id": analytics.match_id,
            "duration": analytics.duration,
            "phase_analysis": analytics.phase_analysis,
            "momentum_shifts": analytics.momentum_shifts,
            "key_decisions": analytics.key_decisions,
            "player_analytics": {
                player_id: {
                    "performance_score": player.performance_score,
                    "strengths": player.strengths,
                    "weaknesses": player.weaknesses,
                    "recommendations": player.recommendations
                }
                for player_id, player in analytics.player_analytics.items()
            },
            "team_analytics": {
                team_id: {
                    "composition_score": team.composition_score,
                    "synergy_rating": team.synergy_rating,
                    "objective_control": team.objective_control,
                    "teamfight_potential": team.teamfight_potential,
                    "scaling_potential": team.scaling_potential
                }
                for team_id, team in analytics.team_analytics.items()
            },
            "predictive_insights": analytics.predictive_insights
        }
    
    def _generate_output_path(self, match: Union[HistoricalMatch, LiveMatch], options: ExportOptions) -> str:
        """Generate output file path."""
        match_id = getattr(match, 'match_id', getattr(match, 'game_id', 'unknown'))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"match_{match_id}_{options.export_type.value}_{timestamp}"
        
        if options.format == ExportFormat.JSON:
            filename += ".json"
        elif options.format == ExportFormat.CSV:
            filename += ".csv"
        elif options.format == ExportFormat.EXCEL:
            filename += ".xlsx"
        elif options.format == ExportFormat.HTML:
            filename += ".html"
        elif options.format == ExportFormat.MARKDOWN:
            filename += ".md"
        
        if options.compress:
            filename += ".zip"
        
        return str(Path(config.data.app_cache_dir) / "exports" / filename)
    
    async def _export_json(self, data: Dict[str, Any], output_path: str, options: ExportOptions) -> ExportResult:
        """Export data as JSON."""
        try:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            
            file_size = Path(output_path).stat().st_size
            
            return ExportResult(
                success=True,
                file_path=output_path,
                file_size=file_size,
                metadata={
                    "format": "json",
                    "records": len(data.get("participants", [])),
                    "exported_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ExportResult(success=False, error_message=str(e))
    
    async def _export_csv(self, data: Dict[str, Any], output_path: str, options: ExportOptions) -> ExportResult:
        """Export data as CSV."""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Create multiple CSV files for different data types
            if options.compress:
                # Create ZIP file with multiple CSVs
                zip_path = output_path.replace('.csv', '.zip')
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    # Participants CSV
                    participants_df = pd.DataFrame(data["participants"])
                    participants_csv = participants_df.to_csv(index=False)
                    zipf.writestr("participants.csv", participants_csv)
                    
                    # Timeline CSV
                    if "timeline" in data:
                        timeline_df = pd.DataFrame(data["timeline"])
                        timeline_csv = timeline_df.to_csv(index=False)
                        zipf.writestr("timeline.csv", timeline_csv)
                    
                    # Analytics CSV
                    if "analytics" in data:
                        analytics_data = data["analytics"]
                        player_analytics_df = pd.DataFrame([
                            {
                                "player_id": player_id,
                                "performance_score": player_data["performance_score"],
                                "strengths": "; ".join(player_data["strengths"]),
                                "weaknesses": "; ".join(player_data["weaknesses"])
                            }
                            for player_id, player_data in analytics_data["player_analytics"].items()
                        ])
                        analytics_csv = player_analytics_df.to_csv(index=False)
                        zipf.writestr("analytics.csv", analytics_csv)
                
                file_size = Path(zip_path).stat().st_size
                return ExportResult(
                    success=True,
                    file_path=zip_path,
                    file_size=file_size,
                    metadata={"format": "csv_zip", "files": ["participants.csv", "timeline.csv", "analytics.csv"]}
                )
            else:
                # Single CSV file
                participants_df = pd.DataFrame(data["participants"])
                participants_df.to_csv(output_path, index=False)
                
                file_size = Path(output_path).stat().st_size
                return ExportResult(
                    success=True,
                    file_path=output_path,
                    file_size=file_size,
                    metadata={"format": "csv", "records": len(participants_df)}
                )
                
        except Exception as e:
            return ExportResult(success=False, error_message=str(e))
    
    async def _export_excel(self, data: Dict[str, Any], output_path: str, options: ExportOptions) -> ExportResult:
        """Export data as Excel file."""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Participants sheet
                participants_df = pd.DataFrame(data["participants"])
                participants_df.to_excel(writer, sheet_name='Participants', index=False)
                
                # Timeline sheet
                if "timeline" in data:
                    timeline_df = pd.DataFrame(data["timeline"])
                    timeline_df.to_excel(writer, sheet_name='Timeline', index=False)
                
                # Analytics sheet
                if "analytics" in data:
                    analytics_data = data["analytics"]
                    player_analytics_df = pd.DataFrame([
                        {
                            "player_id": player_id,
                            "performance_score": player_data["performance_score"],
                            "strengths": "; ".join(player_data["strengths"]),
                            "weaknesses": "; ".join(player_data["weaknesses"])
                        }
                        for player_id, player_data in analytics_data["player_analytics"].items()
                    ])
                    player_analytics_df.to_excel(writer, sheet_name='Player Analytics', index=False)
                
                # Match info sheet
                match_info_df = pd.DataFrame([data["match_info"]])
                match_info_df.to_excel(writer, sheet_name='Match Info', index=False)
            
            file_size = Path(output_path).stat().st_size
            
            return ExportResult(
                success=True,
                file_path=output_path,
                file_size=file_size,
                metadata={"format": "excel", "sheets": ["Participants", "Timeline", "Analytics", "Match Info"]}
            )
            
        except Exception as e:
            return ExportResult(success=False, error_message=str(e))
    
    async def _export_html(self, data: Dict[str, Any], output_path: str, options: ExportOptions) -> ExportResult:
        """Export data as HTML report."""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            html_content = self._generate_html_report(data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            file_size = Path(output_path).stat().st_size
            
            return ExportResult(
                success=True,
                file_path=output_path,
                file_size=file_size,
                metadata={"format": "html", "sections": ["match_info", "participants", "timeline", "analytics"]}
            )
            
        except Exception as e:
            return ExportResult(success=False, error_message=str(e))
    
    async def _export_markdown(self, data: Dict[str, Any], output_path: str, options: ExportOptions) -> ExportResult:
        """Export data as Markdown report."""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            markdown_content = self._generate_markdown_report(data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            file_size = Path(output_path).stat().st_size
            
            return ExportResult(
                success=True,
                file_path=output_path,
                file_size=file_size,
                metadata={"format": "markdown", "sections": ["match_info", "participants", "timeline", "analytics"]}
            )
            
        except Exception as e:
            return ExportResult(success=False, error_message=str(e))
    
    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report content."""
        match_info = data["match_info"]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Match Report - {match_info['match_id']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #1e3a8a; color: white; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .highlight {{ background-color: #fff3cd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>League of Legends Match Report</h1>
                <p>Match ID: {match_info['match_id']}</p>
                <p>Duration: {match_info['duration']} seconds</p>
                <p>Game Mode: {match_info['game_mode']}</p>
            </div>
            
            <div class="section">
                <h2>Participants</h2>
                <table>
                    <tr>
                        <th>Summoner</th>
                        <th>Champion</th>
                        <th>Role</th>
                        <th>K/D/A</th>
                        <th>CS</th>
                        <th>Gold</th>
                    </tr>
        """
        
        for participant in data["participants"]:
            stats = participant["stats"]
            html += f"""
                    <tr>
                        <td>{participant['summoner_name']}</td>
                        <td>{participant['champion_name']}</td>
                        <td>{participant['role']}</td>
                        <td>{stats['kills']}/{stats['deaths']}/{stats['assists']}</td>
                        <td>{stats['cs']}</td>
                        <td>{stats['gold_earned']}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
        """
        
        if "analytics" in data:
            html += """
            <div class="section">
                <h2>Analytics</h2>
                <p>Performance analysis and insights would be displayed here.</p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate Markdown report content."""
        match_info = data["match_info"]
        
        markdown = f"""# League of Legends Match Report

## Match Information
- **Match ID**: {match_info['match_id']}
- **Duration**: {match_info['duration']} seconds
- **Game Mode**: {match_info['game_mode']}
- **Creation Time**: {match_info['creation_time']}

## Participants

| Summoner | Champion | Role | K/D/A | CS | Gold |
|----------|----------|------|-------|----|----- |
"""
        
        for participant in data["participants"]:
            stats = participant["stats"]
            markdown += f"| {participant['summoner_name']} | {participant['champion_name']} | {participant['role']} | {stats['kills']}/{stats['deaths']}/{stats['assists']} | {stats['cs']} | {stats['gold_earned']} |\n"
        
        if "analytics" in data:
            markdown += """
## Analytics

Performance analysis and insights would be included here.

"""
        
        return markdown
    
    async def _compress_export(self, result: ExportResult, options: ExportOptions) -> ExportResult:
        """Compress export file."""
        try:
            if result.file_path.endswith('.zip'):
                return result  # Already compressed
            
            zip_path = result.file_path + '.zip'
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(result.file_path, Path(result.file_path).name)
            
            # Update result with compressed file info
            result.file_path = zip_path
            result.file_size = Path(zip_path).stat().st_size
            result.metadata["compressed"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return result


class ReplayManager:
    """Manages match replay functionality."""
    
    def __init__(self):
        self.exporter = MatchDataExporter()
    
    async def initialize(self):
        """Initialize the replay manager."""
        await self.exporter.initialize()
    
    async def create_replay_package(
        self, 
        match: Union[HistoricalMatch, LiveMatch],
        include_analysis: bool = True
    ) -> ExportResult:
        """
        Create a comprehensive replay package.
        
        Args:
            match: Match to create replay for
            include_analysis: Whether to include detailed analysis
            
        Returns:
            ExportResult with replay package information
        """
        options = ExportOptions(
            format=ExportFormat.JSON,
            export_type=ExportType.COMPREHENSIVE,
            include_timeline=True,
            include_analytics=include_analysis,
            include_highlights=True,
            include_chat_log=True,
            compress=True
        )
        
        return await self.exporter.export_match(match, options)
    
    async def generate_replay_summary(self, match: Union[HistoricalMatch, LiveMatch]) -> str:
        """Generate a text summary of the replay."""
        try:
            # Get match analysis
            analyzer = await get_match_analyzer()
            analytics = await analyzer.analyze_match(match)
            
            # Generate summary
            summary = f"Match Summary for {getattr(match, 'match_id', 'Unknown')}\n\n"
            summary += f"Duration: {analytics.duration} seconds\n"
            summary += f"Game Mode: {match.game_mode.value}\n\n"
            
            # Add key highlights
            if analytics.momentum_shifts:
                summary += "Key Moments:\n"
                for shift in analytics.momentum_shifts[:3]:
                    summary += f"- {shift['description']} at {shift['timestamp']}ms\n"
                summary += "\n"
            
            # Add player performance highlights
            summary += "Top Performers:\n"
            top_players = sorted(
                analytics.player_analytics.items(),
                key=lambda x: x[1].performance_score,
                reverse=True
            )[:3]
            
            for player_id, player_analytics in top_players:
                summary += f"- {player_id}: {player_analytics.performance_score:.2f} performance score\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate replay summary: {e}")
            return f"Error generating summary: {e}"


# Global instances
_match_exporter: Optional[MatchDataExporter] = None
_replay_manager: Optional[ReplayManager] = None


async def get_match_exporter() -> MatchDataExporter:
    """Get the global match exporter instance."""
    global _match_exporter
    if _match_exporter is None:
        _match_exporter = MatchDataExporter()
        await _match_exporter.initialize()
    return _match_exporter


async def get_replay_manager() -> ReplayManager:
    """Get the global replay manager instance."""
    global _replay_manager
    if _replay_manager is None:
        _replay_manager = ReplayManager()
        await _replay_manager.initialize()
    return _replay_manager


# Utility functions
async def export_match_data(
    match: Union[HistoricalMatch, LiveMatch],
    format: ExportFormat = ExportFormat.JSON,
    include_analytics: bool = True
) -> ExportResult:
    """Simple function to export match data."""
    exporter = await get_match_exporter()
    options = ExportOptions(
        format=format,
        export_type=ExportType.MATCH_DATA,
        include_analytics=include_analytics
    )
    return await exporter.export_match(match, options)


async def create_match_replay(match: Union[HistoricalMatch, LiveMatch]) -> ExportResult:
    """Create a comprehensive match replay package."""
    replay_manager = await get_replay_manager()
    return await replay_manager.create_replay_package(match)


if __name__ == "__main__":
    async def main():
        # Test the export system
        exporter = await get_match_exporter()
        print("Match exporter initialized successfully")
        
        replay_manager = await get_replay_manager()
        print("Replay manager initialized successfully")
    
    asyncio.run(main())
