from models import db, Rule

def create_rule(rule_name, rule_string):
    try:
        rule = Rule(name=rule_name, expression=rule_string)
        db.session.add(rule)
        db.session.commit()
        return rule
    except Exception as e:
        print(f"Error creating rule: {e}")
        return None

def combine_rules(combined_rule_name, rule_names):
    try:
        rules = Rule.query.filter(Rule.name.in_(rule_names)).all()
        combined_expression = " and ".join([rule.expression for rule in rules])
        combined_rule = Rule(name=combined_rule_name, expression=combined_expression)
        db.session.add(combined_rule)
        db.session.commit()
        return combined_rule
    except Exception as e:
        print(f"Error combining rules: {e}")
        return None

def evaluate_rule(rule_name, attributes):
    try:
        rule = Rule.query.filter_by(name=rule_name).first()
        if not rule:
            return False
        # Example of evaluating the rule
        # This needs to be adapted to the rule format and evaluation logic you use
        # For now, it's a placeholder
        return eval(rule.expression, {}, attributes)
    except Exception as e:
        print(f"Error evaluating rule: {e}")
        return False

def modify_rule(rule_name, new_rule_string):
    try:
        rule = Rule.query.filter_by(name=rule_name).first()
        if rule:
            rule.expression = new_rule_string
            db.session.commit()
    except Exception as e:
        print(f"Error modifying rule: {e}")
