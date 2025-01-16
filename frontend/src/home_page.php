<?php
session_start();

// Database connection parameters
$servername = "localhost";
$username = "backend";
$password = "cobraSpitfire78!";
$dbname = "Capstone";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check if the user is signed in by checking the session variable
if (isset($_SESSION['User_ID'])) {
    // User is signed in, get the user's email from the session
    $user_email = $_SESSION['Email']; // Adjust to match the correct session variable
} else {
    $user_email = null; // Set to null or empty string for display purposes
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home Page</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <style>
        /* Existing styles */
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #282c34; /* Dark background */
            color: #c0c0c0; /* Light grey text */
            text-align: center;
            padding: 0;
            margin: 0;
        }

        #map {
            height: 475px; /* Size of the map */
            margin-top: 15px;
            width: 1100px;
            margin-left: auto;
            margin-right: auto;
        }
        h1 {
            color: #61dafb; /* Robotic blue */
        }

        .top-bar {
            background-color: #1e90ff; /* Darker blue */
            color: white;
            padding: 10px 0;
            text-align: center;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
            display: flex;
            justify-content: center; /* Centers the links horizontally */
        }

        .top-bar a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            font-size: 16px;
        }

        .top-bar a:hover {
            background-color: #61dafb; /* Robotic blue */
            border-radius: 5px;
        }

        .content {
            margin-top: 60px; /* Space for the top bar */
            padding: 20px; /* Optional: Adds padding around the content */
        }

        button {
            cursor: pointer;
            background-color: #61dafb; /* Robotic blue */
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            transition: background-color 0.3s;
            margin-top: 20px;
        }

        button:hover {
            background-color: #1e90ff; /* Darker blue on hover */
        }
    </style>
</head>
<body>

<div class="top-bar">
    <a href="requests.php">Data Requests</a>
    <a href="help.php">Resources</a>
    <a href="settings.php">Account Settings</a>
    <a href="logout.php">Logout</a>
</div>

<div class="content">
    <h1>Welcome to the Home Page!</h1>

    <?php if ($user_email): ?>
        <!-- Display user's email if signed in -->
        <p>Signed in as: <?php echo htmlspecialchars($user_email); ?></p>

        <h2>Click on the map to select your location</h2>

        <!-- Map Container -->
        <div id="map"></div>

        <p id="location-status"></p>

        <!-- Submit Button -->
        <button id="save-location-btn" onclick="submitCoordinates()">Save Location</button>

    <?php else: ?>
        <p>You are not signed in. Please <a href="login.php">log in</a> to continue.</p>
    <?php endif; ?>
</div>

<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
<script>
    var map = L.map('map').setView([37, -76.4], 13); // Default starting location
    var selectedLat = null;
    var selectedLon = null;

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Event listener for map clicks
    map.on('click', function(e) {
        selectedLat = e.latlng.lat;
        selectedLon = e.latlng.lng;

        // Display the selected coordinates
        document.getElementById("location-status").innerText = `Latitude: ${selectedLat}, Longitude: ${selectedLon}`;
    });

    // Function to submit the coordinates when the button is clicked
    function submitCoordinates() {
        if (selectedLat !== null && selectedLon !== null) {
            const xhr = new XMLHttpRequest();
            xhr.open("POST", "save_location.php", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.onload = function() {
                if (xhr.status == 200) {
                    alert("Location saved successfully!");
                } else {
                    alert("Error saving location.");
                }
            };
            xhr.send(`latitude=${selectedLat}&longitude=${selectedLon}`);
        } else {
            alert("Please click on the map to select a location first.");
        }
    }
</script>

</body>
</html>

