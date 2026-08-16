const API_BASE_URL = 'http://127.0.0.1:8000/api/debate';

export async function createDebate(topic: string, student_position: 'for' | 'against') {
  const res = await fetch(`${API_BASE_URL}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, student_position }),
  });
  if (!res.ok) throw new Error('Failed to create debate');
  return res.json();
}

export async function submitTurn(debateId: string, student_argument: string) {
  const res = await fetch(`${API_BASE_URL}/${debateId}/turn`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ student_argument }),
  });
  if (!res.ok) throw new Error('Failed to submit turn');
  return res.json();
}

export async function scoreDebate(debateId: string) {
  const res = await fetch(`${API_BASE_URL}/${debateId}/score`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to score debate');
  return res.json();
}
