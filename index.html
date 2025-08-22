const express = require('express');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process'); // For running ImageMagick

// --- EXPRESS SERVER SETUP ---
const app = express();
const port = 3000;
app.use(express.json());
app.use(express.static(__dirname));

// --- PAGE ROUTING ---
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));

// --- WORKBENCH API ROUTE ---
app.post('/quantize-image', (req, res) => {
  const { imageName, colorCount } = req.body;
  const inputPath = path.join(__dirname, imageName);
  const outputPath = path.join(__dirname, `quantized-${imageName}`);
  const command = `magick "${inputPath}" +dither -colors ${colorCount} "${outputPath}"`;
  
  console.log(`Running ImageMagick: ${command}`);
  try {
    execSync(command);
    const resultBuffer = fs.readFileSync(outputPath);
    const base64Image = `data:image/png;base64,${resultBuffer.toString('base64')}`;
    res.json({ imageSrc: base64Image });
    fs.unlinkSync(outputPath); // Clean up the temporary file
  } catch (error) {
    console.error("ImageMagick Error:", error.stderr ? error.stderr.toString() : error.message);
    res.status(500).json({ error: "Failed to process image." });
  }
});

// --- START SERVER ---
app.listen(port, () => {
  console.log(`Workbench server running.`);
});
