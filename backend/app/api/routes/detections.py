import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.crud import (
    get_detection_by_id,
    get_detections,
    get_detections_by_confidence,
    get_detections_by_person_id,
    get_detections_by_time_range,
    get_latest_detection_by_person_id,
)
from app.models import Detection, DetectionPublic, DetectionsPublic

router = APIRouter(prefix="/detections", tags=["detections"])


@router.get("/", response_model=DetectionsPublic)
def read_detections(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
) -> Any:
    """
    Retrieve detections with pagination.
    
    Returns a list of all detection records with pagination support.
    """
    detections = get_detections(session=session, skip=skip, limit=limit)
    
    # Get total count
    count_statement = select(func.count()).select_from(Detection)
    count = session.exec(count_statement).one()
    
    return DetectionsPublic(data=detections, count=count)


@router.get("/stats/summary", response_model=dict)
def get_detection_summary(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get overall detection statistics for dashboard overview.
    
    Returns:
        - Total detection count
        - Unique persons detected
        - Average confidence score
        - Detection count in last 24 hours
        - Detection count in last hour
    """
    # Total detections
    total_count_statement = select(func.count()).select_from(Detection)
    total_count = session.exec(total_count_statement).one()
    
    # Unique persons
    unique_persons_statement = select(func.count(func.distinct(Detection.person_id)))
    unique_persons = session.exec(unique_persons_statement).one()
    
    # Average confidence
    avg_confidence_statement = select(func.avg(Detection.confidence))
    avg_confidence = session.exec(avg_confidence_statement).one()
    
    # Detections in last 24 hours
    now = datetime.now(timezone.utc)
    last_24h_time = now - timedelta(hours=24)
    last_24h_statement = select(func.count()).select_from(Detection).where(
        Detection.first_detection_time >= last_24h_time
    )
    last_24h_count = session.exec(last_24h_statement).one()
    
    # Detections in last hour
    last_1h_time = now - timedelta(hours=1)
    last_1h_statement = select(func.count()).select_from(Detection).where(
        Detection.first_detection_time >= last_1h_time
    )
    last_1h_count = session.exec(last_1h_statement).one()
    
    return {
        "total_detections": total_count,
        "unique_persons": unique_persons,
        "average_confidence": round(float(avg_confidence or 0), 2),
        "detections_last_24h": last_24h_count,
        "detections_last_hour": last_1h_count,
    }


@router.get("/stats/by-person", response_model=list[dict])
def get_detections_by_person_stats(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of persons to return"),
) -> Any:
    """
    Get detection statistics grouped by person ID.
    
    Returns statistics for each person including:
    - Person ID
    - Total detection count
    - Average confidence
    - First and last detection times
    - Total time tracked
    """
    # Query to get stats per person
    statement = (
        select(
            Detection.person_id,
            func.count(Detection.id).label("detection_count"),
            func.avg(Detection.confidence).label("avg_confidence"),
            func.min(Detection.first_detection_time).label("first_seen"),
            func.max(Detection.last_detection_time).label("last_seen"),
            func.max(Detection.elapsed_time).label("total_time_tracked"),
        )
        .group_by(Detection.person_id)
        .order_by(func.count(Detection.id).desc())
        .limit(limit)
    )
    
    results = session.exec(statement).all()
    
    return [
        {
            "person_id": row.person_id,
            "detection_count": row.detection_count,
            "avg_confidence": round(float(row.avg_confidence), 2),
            "first_seen": row.first_seen.isoformat(),
            "last_seen": row.last_seen.isoformat(),
            "total_time_tracked": round(float(row.total_time_tracked), 2),
        }
        for row in results
    ]


@router.get("/stats/timeline", response_model=list[dict])
def get_detection_timeline(
    session: SessionDep,
    current_user: CurrentUser,
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    interval_minutes: int = Query(60, ge=5, le=1440, description="Interval in minutes for grouping"),
) -> Any:
    """
    Get detection timeline for the last N hours, grouped by time intervals.
    
    Useful for creating time-series charts showing detection activity over time.
    """
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)
    
    # Get all detections in the time range
    detections = get_detections_by_time_range(
        session=session,
        start_time=start_time,
        end_time=now
    )
    
    # Group by intervals
    timeline = {}
    interval_seconds = interval_minutes * 60
    
    for detection in detections:
        # Round datetime down to nearest interval
        detection_time = detection.first_detection_time
        if detection_time.tzinfo is None:
            detection_time = detection_time.replace(tzinfo=timezone.utc)
        
        # Calculate seconds since epoch for interval calculation
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        seconds_since_epoch = int((detection_time - epoch).total_seconds())
        interval_timestamp = (seconds_since_epoch // interval_seconds) * interval_seconds
        interval_time = epoch + timedelta(seconds=interval_timestamp)
        interval_key = interval_time.isoformat()
        
        if interval_key not in timeline:
            timeline[interval_key] = {
                "timestamp": interval_key,
                "count": 0,
                "unique_persons": set(),
                "avg_confidence": [],
            }
        
        timeline[interval_key]["count"] += 1
        timeline[interval_key]["unique_persons"].add(detection.person_id)
        timeline[interval_key]["avg_confidence"].append(detection.confidence)
    
    # Convert to list and calculate averages
    result = []
    for timestamp in sorted(timeline.keys()):
        data = timeline[timestamp]
        result.append({
            "timestamp": timestamp,
            "detection_count": data["count"],
            "unique_persons": len(data["unique_persons"]),
            "avg_confidence": round(
                sum(data["avg_confidence"]) / len(data["avg_confidence"]), 2
            ) if data["avg_confidence"] else 0,
        })
    
    return result


@router.get("/stats/active-persons", response_model=list[dict])
def get_active_persons(
    session: SessionDep,
    current_user: CurrentUser,
    minutes: int = Query(5, ge=1, le=1440, description="Time window in minutes to consider a person active"),
) -> Any:
    """
    Get currently active persons (detected within the last N minutes).
    
    Returns the latest detection for each person who was detected recently.
    """
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    
    # Get all unique person IDs detected recently
    statement = (
        select(Detection.person_id)
        .where(Detection.last_detection_time >= cutoff_time)
        .distinct()
    )
    
    person_ids = session.exec(statement).all()
    
    # Get latest detection for each person
    active_persons = []
    for person_id in person_ids:
        latest_detection = get_latest_detection_by_person_id(
            session=session,
            person_id=person_id
        )
        if latest_detection:
            # Ensure timezone awareness
            last_seen = latest_detection.last_detection_time
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
            
            active_persons.append({
                "person_id": latest_detection.person_id,
                "last_seen": last_seen.isoformat(),
                "confidence": round(latest_detection.confidence, 2),
                "elapsed_time": round(latest_detection.elapsed_time, 2),
                "bbox": {
                    "x1": latest_detection.bbox_x1,
                    "y1": latest_detection.bbox_y1,
                    "x2": latest_detection.bbox_x2,
                    "y2": latest_detection.bbox_y2,
                },
            })
    
    # Sort by last_seen descending
    active_persons.sort(key=lambda x: x["last_seen"], reverse=True)
    
    return active_persons


@router.get("/stats/confidence-distribution", response_model=dict)
def get_confidence_distribution(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get distribution of detection confidence scores.
    
    Returns counts of detections in different confidence ranges.
    """
    ranges = [
        (0.0, 0.5, "low"),
        (0.5, 0.7, "medium"),
        (0.7, 0.85, "high"),
        (0.85, 1.0, "very_high"),
    ]
    
    distribution = {}
    for min_conf, max_conf, label in ranges:
        statement = (
            select(func.count())
            .select_from(Detection)
            .where(Detection.confidence >= min_conf, Detection.confidence < max_conf)
        )
        count = session.exec(statement).one()
        distribution[label] = {
            "range": f"{min_conf}-{max_conf}",
            "count": count,
        }
    
    return distribution


@router.get("/person/{person_id}", response_model=DetectionsPublic)
def read_detections_by_person(
    person_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get all detections for a specific person ID.
    
    Returns all detection records associated with a particular person.
    """
    detections = get_detections_by_person_id(session=session, person_id=person_id)
    
    if not detections:
        raise HTTPException(
            status_code=404,
            detail=f"No detections found for person_id: {person_id}"
        )
    
    return DetectionsPublic(data=detections, count=len(detections))


@router.get("/person/{person_id}/latest", response_model=DetectionPublic)
def read_latest_detection_by_person(
    person_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get the most recent detection for a specific person ID.
    """
    detection = get_latest_detection_by_person_id(session=session, person_id=person_id)
    
    if not detection:
        raise HTTPException(
            status_code=404,
            detail=f"No detections found for person_id: {person_id}"
        )
    
    return detection


@router.get("/time-range", response_model=DetectionsPublic)
def read_detections_by_time_range(
    session: SessionDep,
    current_user: CurrentUser,
    start_time: str = Query(..., description="ISO datetime string for start of range (e.g., '2024-01-01T00:00:00Z')"),
    end_time: str = Query(..., description="ISO datetime string for end of range (e.g., '2024-01-01T23:59:59Z')"),
) -> Any:
    """
    Get detections within a specific time range.
    
    Args:
        start_time: ISO datetime string for the start of the range
        end_time: ISO datetime string for the end of the range
    """
    try:
        # Parse ISO datetime strings
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid datetime format: {str(e)}"
        )
    
    if start_dt >= end_dt:
        raise HTTPException(
            status_code=400,
            detail="start_time must be less than end_time"
        )
    
    detections = get_detections_by_time_range(
        session=session,
        start_time=start_dt,
        end_time=end_dt
    )
    
    return DetectionsPublic(data=detections, count=len(detections))


@router.get("/by-confidence", response_model=DetectionsPublic)
def read_detections_by_confidence(
    session: SessionDep,
    current_user: CurrentUser,
    min_confidence: float = Query(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold"),
) -> Any:
    """
    Get detections with confidence above a specified threshold.
    """
    detections = get_detections_by_confidence(
        session=session,
        min_confidence=min_confidence
    )
    
    return DetectionsPublic(data=detections, count=len(detections))


@router.get("/{detection_id}", response_model=DetectionPublic)
def read_detection(
    detection_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get a specific detection by ID.
    """
    detection = get_detection_by_id(session=session, detection_id=detection_id)
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    return detection