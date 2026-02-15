function ConstraintsForm({
  nVars,
  constraints,
  setConstraints,
  nonneg,
  setNonneg,
}) {
  const addConstraint = () => {
    setConstraints([
      ...constraints,
      { a: Array(nVars).fill(""), sense: "<=", b: "" },
    ]);
  };

  const updateConstraint = (index, field, value, varIndex = null) => {
    const newConstraints = [...constraints];
    const numValue = value === "" ? "" : parseFloat(value);
    if (field === "a") {
      newConstraints[index].a[varIndex] = numValue;
    } else if (field === "b") {
      newConstraints[index][field] = numValue;
    } else {
      newConstraints[index][field] = value;
    }
    setConstraints(newConstraints);
  };

  const removeConstraint = index => {
    setConstraints(constraints.filter((_, i) => i !== index));
  };

  return (
    <div>
      <h3>Constraints</h3>

      <label>
        Variables Non-Negative:
        <input
          type="checkbox"
          checked={nonneg}
          onChange={e => setNonneg(e.target.checked)}
        />
      </label>

      {constraints.map((con, i) => (
        <div key={i} style={{ marginBottom: 10 }}>
          {con.a.map((val, j) => (
            <input
              key={j}
              type="number"
              value={val}
              onChange={e => updateConstraint(i, "a", e.target.value, j)}
              style={{ width: 60 }}
            />
          ))}
          <select
            value={con.sense}
            onChange={e => updateConstraint(i, "sense", e.target.value)}
          >
            <option value="<=">&le;</option>
            <option value=">=">&ge;</option>
            <option value="=">=</option>
          </select>
          <input
            type="number"
            value={con.b}
            onChange={e => updateConstraint(i, "b", e.target.value)}
          />
          <button onClick={() => removeConstraint(i)}>Remove</button>
        </div>
      ))}

      <button onClick={addConstraint}>+ Add Constraint</button>
    </div>
  );
}

export default ConstraintsForm;
