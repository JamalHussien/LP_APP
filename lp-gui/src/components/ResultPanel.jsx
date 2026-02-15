function ResultPanel({ result, imageUrl }) {
  return (
    <div style={{ marginTop: 30 }}>
      {result && (
        <div>
          <h3>Numerical Result</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      {imageUrl && (
        <div>
          <h3>Graphical Result</h3>
          <img src={imageUrl} alt="LP Graph" style={{ maxWidth: "100%" }} />
        </div>
      )}
    </div>
  );
}

export default ResultPanel;
