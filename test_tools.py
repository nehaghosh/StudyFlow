from memory import AgentMemory
from tools import StudyTools


def test_add_task():
    memory = AgentMemory()
    tools = StudyTools(memory)

    result = tools.add_task(
        "DBMS",
        "Complete normalization assignment",
        "2026-09-08",
        4
    )

    assert result["success"] is True
    assert len(memory.get_tasks()) == 1

    print("✅ test_add_task passed")


def test_schedule():
    memory = AgentMemory()
    tools = StudyTools(memory)

    tools.add_task(
        "DBMS",
        "Normalization assignment",
        "2026-09-08",
        4
    )

    result = tools.build_schedule(
        daily_hours=3,
        start_date="2026-09-04"
    )

    assert result["success"] is True
    assert len(result["schedule"]) > 0

    print("✅ test_schedule passed")


def test_custom_hours():
    memory = AgentMemory()
    tools = StudyTools(memory)

    tools.add_task(
        "AI",
        "Complete AI project",
        "2026-09-10",
        6
    )

    result = tools.build_schedule(
        daily_hours=3,
        start_date="2026-09-04",
        custom_hours={
            "2026-09-04": 6
        }
    )

    assert result["success"] is True

    # Check that the first day can use the customized 6 hours
    first_day = [
        item for item in result["schedule"]
        if item["date"] == "2026-09-04"
    ]

    total_hours = sum(
        item["hours"] for item in first_day
    )

    assert total_hours == 6

    print("✅ test_custom_hours passed")


def test_invalid_deadline():
    memory = AgentMemory()
    tools = StudyTools(memory)

    result = tools.add_task(
        "DBMS",
        "Test assignment",
        "wrong-date",
        3
    )

    assert result["success"] is False

    print("✅ test_invalid_deadline passed")


def test_no_tasks():
    memory = AgentMemory()
    tools = StudyTools(memory)

    result = tools.build_schedule(
        daily_hours=3,
        start_date="2026-09-04"
    )

    assert result["success"] is False

    print("✅ test_no_tasks passed")


if __name__ == "__main__":

    test_add_task()
    test_schedule()
    test_custom_hours()
    test_invalid_deadline()
    test_no_tasks()

    print("\n🎉 ALL TESTS PASSED!")