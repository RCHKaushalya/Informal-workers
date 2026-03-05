const API = 'https://informal-worker.onrender.com';

async function loadJobs() {
    const response = await fetch(`${API}/jobs/`);
    if (!response.ok) {
        alert('Failed to load jobs');
        return;
    }
    const data = await response.json();
    const jobs = data.jobs;

    const container = document.getElementById('jobs');
    container.innerHTML = '';

    jobs.forEach(job => {
        const card = document.createElement('div');
        card.className = 'job-card';

        card.innerHTML = `
            <h3>${job.title}</h3>
            <p>${job.description}</p>

            <button onclick="acceptJob(${job.id})">👍 Accept</button>
            <button onclick="rejectJob(${job.id})">❌ Reject</button>
        `
        container.appendChild(card);
    })
}

async function acceptJob(job_id) {
    await fetch(`${API}/respond-job`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            job_id: job_id,
            worker_id: 1,
            response: 'liked' })
    });

    alert('You accepted the job!');
}

async function rejectJob(job_id) {
    await fetch(`${API}/respond-job`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            job_id: job_id,
            worker_id: 1,
            response: 'rejected' })
    });

    alert('You rejected the job!');
}

loadJobs();