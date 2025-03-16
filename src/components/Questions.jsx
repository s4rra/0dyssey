import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Questions() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const API_URL = "http://127.0.0.1:8080/api/questions";

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in first.");
      navigate("/login");
      return;
    }

    fetch(API_URL, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => {
        setQuestions(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching questions:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2>Questions</h2>
      <ul>
        {questions.map((question) => (
          <li key={question.unitID}>
            <h3>{question.unitName}</h3>
            {question.RefSubUnit && question.RefSubUnit.length > 0 ? (
              <ul>
                {question.RefSubUnit.map((subUnit) => (
                  <li key={subUnit.subUnitID}>
                    <button
                      onClick={() => navigate(`/subunit/${subUnit.subUnitID}/questions`)}
                      style={{ background: "none", border: "none", color: "blue", textDecoration: "underline", cursor: "pointer" }}
                    >
                      {subUnit.subUnitName}
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No available</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Questions;
