import streamlit as st
import json

st.set_page_config(page_title="Scholarship Advisory System", page_icon="🎓", layout="centered")

DEFAULT_RULES = [
    {
        "name": "Top merit candidate",
        "priority": 100,
        "conditions": [
            ["cgpa", ">=", 3.7],
            ["co_curricular_score", ">=", 80],
            ["family_income", "<=", 8000],
            ["disciplinary_actions", "==", 0]
        ],
        "action": {
            "decision": "AWARD_FULL",
            "reason": "Excellent academic & co-curricular performance, with acceptable need"
        }
    },
    {
        "name": "Good candidate - partial scholarship",
        "priority": 80,
        "conditions": [
            ["cgpa", ">=", 3.3],
            ["co_curricular_score", ">=", 60],
            ["family_income", "<=", 12000],
            ["disciplinary_actions", "<=", 1]
        ],
        "action": {
            "decision": "AWARD_PARTIAL",
            "reason": "Good academic & involvement record with moderate need"
        }
    },
    {
        "name": "Need-based review",
        "priority": 70,
        "conditions": [
            ["cgpa", ">=", 2.5],
            ["family_income", "<=", 4000]
        ],
        "action": {
            "decision": "REVIEW",
            "reason": "High need but borderline academic score"
        }
    },
    {
        "name": "Low CGPA – not eligible",
        "priority": 95,
        "conditions": [
            ["cgpa", "<", 2.5]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "CGPA below minimum scholarship requirement"
        }
    },
    {
        "name": "Serious disciplinary record",
        "priority": 90,
        "conditions": [
            ["disciplinary_actions", ">=", 2]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "Too many disciplinary records"
        }
    }
]

def condition_is_true(facts, condition):
    field, operator, threshold = condition
    if field not in facts:
        raise ValueError(f"Unknown applicant field: {field}")
    value = facts[field]
    if operator == ">=":
        return value >= threshold
    if operator == "<=":
        return value <= threshold
    if operator == ">":
        return value > threshold
    if operator == "<":
        return value < threshold
    if operator == "==":
        return value == threshold
    if operator == "!=":
        return value != threshold
    raise ValueError(f"Unsupported operator: {operator}")

def validate_rules(rules):
    if not isinstance(rules, list):
        raise ValueError("The JSON knowledge base must be a list of rules.")
    required = {"name", "priority", "conditions", "action"}
    for index, rule in enumerate(rules, start=1):
        if not isinstance(rule, dict) or not required.issubset(rule):
            raise ValueError(f"Rule {index} must contain name, priority, conditions and action.")
        if not isinstance(rule["conditions"], list) or not rule["conditions"]:
            raise ValueError(f"Rule {index} must have at least one condition.")
        if not isinstance(rule["action"], dict) or not {"decision", "reason"}.issubset(rule["action"]):
            raise ValueError(f"Rule {index} action must contain decision and reason.")
        for condition in rule["conditions"]:
            if not isinstance(condition, list) or len(condition) != 3:
                raise ValueError(f"Each condition in rule {index} must have 3 items.")

def evaluate_applicant(facts, rules):
    # Highest priority is evaluated first. All conditions in a rule must be true.
    for rule in sorted(rules, key=lambda item: item["priority"], reverse=True):
        if all(condition_is_true(facts, condition) for condition in rule["conditions"]):
            return rule
    return None

st.title("🎓 Scholarship Advisory System")
st.write("A rule-based decision support tool for evaluating scholarship applicants.")
st.info("This application supports committee decisions. Final scholarship approval should be made by the university committee.")

st.header("1. Applicant Information")
with st.form("applicant_form"):
    col1, col2 = st.columns(2)
    with col1:
        cgpa = st.number_input("Cumulative GPA (CGPA)", min_value=0.0, max_value=4.0, value=3.50, step=0.01, format="%.2f")
        family_income = st.number_input("Monthly family income (RM)", min_value=0, value=3000, step=100)
        co_curricular_score = st.number_input("Co-curricular involvement score (0–100)", min_value=0, max_value=100, value=75)
    with col2:
        community_service_hours = st.number_input("Community service hours", min_value=0, value=20, step=1)
        current_semester = st.number_input("Current semester of study", min_value=1, value=3, step=1)
        disciplinary_actions = st.number_input("Number of disciplinary actions", min_value=0, value=0, step=1)
    submitted = st.form_submit_button("Evaluate Scholarship Eligibility", type="primary")

st.header("2. JSON Rule Editor")
st.caption("The editor is preloaded with the five rules provided in the lab report. You may adjust the configuration and click Apply Rules.")
json_text = st.text_area("Edit scholarship rules (JSON)", value=json.dumps(DEFAULT_RULES, indent=4), height=430)
apply_rules = st.button("Apply Rules")

try:
    rules = json.loads(json_text)
    validate_rules(rules)
    st.success(f"JSON knowledge base loaded successfully: {len(rules)} rules.")
except (json.JSONDecodeError, ValueError, TypeError) as error:
    st.error(f"Invalid rule configuration: {error}")
    rules = None

if submitted:
    if rules is None:
        st.warning("Please correct the JSON rules before evaluating the applicant.")
    else:
        facts = {
            "cgpa": cgpa,
            "family_income": family_income,
            "co_curricular_score": co_curricular_score,
            "community_service_hours": community_service_hours,
            "current_semester": current_semester,
            "disciplinary_actions": disciplinary_actions
        }
        try:
            matched_rule = evaluate_applicant(facts, rules)
            st.header("3. Evaluation Result")
            if matched_rule:
                decision = matched_rule["action"]["decision"]
                st.subheader(decision.replace("_", " "))
                st.write("**Matched rule:**", matched_rule["name"])
                st.write("**Reason:**", matched_rule["action"]["reason"])
                st.write("**Priority:**", matched_rule["priority"])
            else:
                st.warning("NO MATCHING RULE: The applicant does not meet any configured rule. Refer the case to the scholarship committee.")
            with st.expander("View applicant facts"):
                st.json(facts)
        except (ValueError, TypeError) as error:
            st.error(f"Could not evaluate rules: {error}")

st.divider()
st.caption("BSD3513 / BSD2513 – Introduction to Artificial Intelligence | Knowledge Representation System")
