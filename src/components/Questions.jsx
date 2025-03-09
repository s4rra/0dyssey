import { useEffect, useState, useRef } from "react";
import axios from "axios";

function Questions() {
    let [questions, setQuestions] = useState([]);
    let [loading, setLoading] = useState(true);
    const API_URL = "http://127.0.0.1:8080/questions";

    useEffect(() => {
        axios
            .get(API_URL)
            .then((response) => {
                setQuestions(response.data);
                setLoading(false);
            })
            .catch((error) => {
                console.error("Error fetching questions:", error);
                setLoading(false);
            });
    }, []);

    if (loading) return <p>Loading...</p>;

    return (
        <div>
            <h1>Questions Page</h1>
            <ul>
                {Object.entries(questions).map(([key, question]) => (
                    <li key={key}>
                        <h3>{question.question}</h3>
                        {question.options && (
                            <ul>
                                {Object.entries(question.options).map(([optKey, optValue]) => (
                                    <li key={optKey}>{optKey}: {optValue}</li>
                                ))}
                            </ul>
                        )}
                        
                    </li>
                ))}
            </ul>
        </div>
    );
}
export default Questions;
