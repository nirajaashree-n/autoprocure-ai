
# This file is JUST a layout designer.
def generate_comparison_table(all_quotes):
    if not all_quotes:
        return "No quotes found for comparison."

    header = "*Current Quotes Comparison Summary*\n"
    table = "```\n"
    table += f"{'VENDOR':<15} | {'PRODUCT':<15} | {'PRICE':<10}\n"
    table += "-" * 45 + "\n"
    
    for q in all_quotes:
        # Tuple mapping from our new DB query:
        # q[1] = Name, q[3] = Item, q[4] = Price
        v = str(q[1])[:15]
        i = str(q[3])[:15]
        p = str(q[4])
        table += f"{v:<15} | {i:<15} | ${p:<10}\n"
    
    table += "```"
    return header + table

