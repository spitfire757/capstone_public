<?php
session_start();

// Check if the user is signed in by checking the session variable
if (isset($_SESSION['User_ID'])) {
    // User is signed in, get the user's email from the session
    $user_email = $_SESSION['Email']; // Adjust to match the correct session variable
} else {
    $user_email = null; // Set to null or empty string for display purposes
}

// Check if the forecast request button was pressed
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['request_forecast'])) {
    $user_id = $_SESSION['User_ID'];
    $weather_parameter = $_POST['weather_parameter'];

    // Database connection parameters
    $servername = "localhost";     // MySQL server (use 'localhost' if on the same server)
    $username = "backend";         // MySQL username
    $password = "cobraSpitfire78!"; // MySQL password
    $dbname = "Capstone";          // Name of your database

    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);
    // Check connection
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    // Query to get User_Lat and User_Lon using User_ID
    $sql = "SELECT User_Lat.Lat AS latitude, User_Lon.Lon AS longitude
            FROM User_Lat
            JOIN User_Lon ON User_Lat.User_ID = User_Lon.User_ID
            WHERE User_Lat.User_ID = ?";

    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $user_id);
    $stmt->execute();
    $stmt->bind_result($latitude, $longitude);
    $stmt->fetch();
    $stmt->close();
    $conn->close();

    if ($latitude === null || $longitude === null) {
        echo "Error: Latitude or Longitude not found for user.";
        exit;
    }

    // NGROK URL of the Raspberry Pi
    $ngrok_url = "https://marmot-chief-toucan.ngrok-free.app"; // Replace with the actual NGROK URL
    

    // Prepare the data to send as an array
// Ensure data is being set and passed correctly
$data = [
    'user_id' => $user_id,
    'latitude' => $latitude,
    'longitude' => $longitude,
    'parameter' => $weather_parameter,
];

$json_data = json_encode($data);

// Initialize cURL request to send data as JSON
$ch = curl_init("$ngrok_url/forecast");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $json_data); // Send JSON data

// Set the Content-Type to application/json
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    "Content-Type: application/json",
    "Content-Length: " . strlen($json_data)
));

$response = curl_exec($ch); // Fetch response from Flask app

if (curl_errno($ch)) {
    $forecast_result = "Error: " . curl_error($ch); // Capture cURL error if it occurs
} else {
    $forecast_result = $response; // Save the Flask response
}

curl_close($ch);


}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Requests Page</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #282c34; /* Dark background */
            color: #c0c0c0; /* Light grey text */
            text-align: center;
            padding: 0;
            margin: 0;
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
            padding: 20px;
            display: flex;
            justify-content: center;
            gap: 20px;
        }

        .half-page {
            width: 45%;
            padding: 20px;
            background-color: #333;
            border-radius: 8px;
        }

        .button {
            padding: 10px 20px;
            background-color: #61dafb;
            border: none;
            color: white;
            cursor: pointer;
            border-radius: 5px;
            font-size: 16px;
        }

        .dropdown {
            margin-top: 10px;
            width: 100%;
            padding: 8px;
            font-size: 16px;
            border-radius: 5px;
        }
    </style>
</head>
<body>

<!-- Top Bar -->
<div class="top-bar">
    <a href="home_page.php">Home</a>
    <a href="settings.php">Account Settings</a>
    <a href="help.php">Resources</a>
    <a href="logout.php">Logout</a>
</div>

<div class="content">
    <!-- Left Section: Request Forecast -->
    <div class="half-page">
        <h2>Request Forecast</h2>
        <form method="POST">
            <!-- Weather Parameter Selection -->
            <select name="weather_parameter" class="dropdown">
                <option value="temperature_2m">temperature_2m</option>
                <option value="relative_humidity_2m">relative_humidity_2m</option>
                <option value="precipitation">precipitation</option>
                <option value="rain">rain</option>
                <option value="weather_code">weather_code</option>
                <option value="surface_pressure">surface_pressure</option>
                <option value="cloud_cover">cloud_cover</option>
                <option value="wind_speed_10m">wind_speed_10m</option>
                <option value="wind_speed_100m">wind_speed_100m</option>
                <option value="wind_direction_10m">wind_direction_10m</option>
                <option value="wind_direction_100m">wind_direction_100m</option>
            </select>
            <br><br>
            <input type="submit" name="request_forecast" value="Request Forecast" class="button">
        </form>

        <!-- Display forecast result if available -->
        <?php if (isset($forecast_result)): ?>
            <div>
                <h3>Forecast Result:</h3>
                <p><?php echo htmlspecialchars($forecast_result); ?></p>
            </div>
        <?php endif; ?>
    </div>

    <!-- Right Section: Request Geodetic Data -->
    <div class="half-page">
        <h2>Request Geodetic Data</h2>
        <form method="POST">
            <input type="submit" name="request_geodetic" value="Request Geodetic Data" class="button">
        </form>
    </div>
</div>

</body>
</html>

