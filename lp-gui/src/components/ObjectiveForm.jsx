function ObjectiveForm({ nVars, objective, setObjective, sense, setSense }) {
  const updateCoeff = (index, value) => {
    const newObj = [...objective];
    newObj[index] = value === "" ? "" : parseFloat(value);
    setObjective(newObj);
  };

  return (
    <div>
      <h3>Objective</h3>

      <select value={sense} onChange={e => setSense(e.target.value)}>
        <option value="maximize">Maximize</option>
        <option value="minimize">Minimize</option>
      </select>

      {objective.map((val, i) => (
        <div key={i}>
          c{i + 1}:
          <input
            type="number"
            value={val}
            onChange={e => updateCoeff(i, e.target.value)}
          />
        </div>
      ))}
    </div>
  );
}

export default ObjectiveForm;
