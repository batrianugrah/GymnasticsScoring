document.addEventListener('DOMContentLoaded', function() {
    const scoreTableBody = document.getElementById('live-score-table');
    async function fetchScores() {
        try {
            const response = await fetch('/api/scores');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const scores = await response.json();
            updateTable(scores);
        } catch (error) {
            console.error("Could not fetch scores:", error);
            scoreTableBody.innerHTML = `<tr><td colspan="9" class="text-danger">Gagal memuat data. Mencoba lagi...</td></tr>`;
        }
    }
    function updateTable(scores) {
        scoreTableBody.innerHTML = '';
        if (scores.length === 0) {
            scoreTableBody.innerHTML = `<tr><td colspan="9">Menunggu skor pertama...</td></tr>`;
            return;
        }
        scores.forEach(score => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${score.rank}</strong></td><td>${score.nama_peserta}</td><td>${score.nama_daerah}</td>
                <td>${score.alat}</td><td>${score.nilai_d}</td><td>${score.nilai_e}</td>
                <td>${score.nilai_a}</td><td>${score.penalti}</td>
                <td><span class="badge bg-primary fs-5">${score.total_nilai}</span></td>
            `;
            scoreTableBody.appendChild(row);
        });
    }
    fetchScores();
    setInterval(fetchScores, 3000); 
});