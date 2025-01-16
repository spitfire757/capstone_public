<?php
session_start();

// Check if the user is signed in by checking the session variable
if (isset($_SESSION['User_ID'])) {
    $user_email = $_SESSION['Email']; // Adjust to match the correct session variable
    $user_id = $_SESSION['User_ID']; // Store the User_ID for later use
} else {
    $user_email = null; // Set to null for display purposes
    $user_id = null; // Ensure we don't proceed if the user is not logged in
}

$forecast_result = null;
$map_image_path = null;

// Check if the user has a map image already generated when the page loads
if ($user_id !== null) {
    // Query for latitude and longitude from the database
    $servername = "localhost";
    $username = "backend";
    $password = "cobraSpitfire78!";
    $dbname = "Capstone";          

    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    // Query to get latitude and longitude for the user
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

    if ($latitude !== null && $longitude !== null) {
        // Check if the map image already exists
        $map_file_name = "{$user_id}_{$weather_parameter}_forecast.gif";
        echo $map_file_name;
        $map_image_path = "/var/www/html/user_maps/$map_file_name"; 

        if (file_exists($map_image_path)) {
            $map_image_path = "https://skyskynthwaml.com/user_maps/$map_file_name"; // Update to the public URL
        } else {
            $map_image_path = null; // Reset if file does not exist
        }
    }
}

// Check if the forecast request button was pressed
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['request_forecast'])) {
    $weather_parameter = $_POST['weather_parameter'];

    if ($user_id !== null && $latitude !== null && $longitude !== null) {
        // NGROK URL of the Raspberry Pi
        $ngrok_url = "https://marmot-chief-toucan.ngrok-free.app"; 

        // Prepare the data to send
        $data = [
            'user_id' => $user_id,
            'latitude' => $latitude,
            'longitude' => $longitude,
            'parameter' => $weather_parameter,
        ];

        $json_data = json_encode($data);

        // Initialize cURL request
        $ch = curl_init("$ngrok_url/forecast");
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $json_data);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array(
            "Content-Type: application/json",
            "Content-Length: " . strlen($json_data)
        ));

        $response = curl_exec($ch);

        if (curl_errno($ch)) {
            $forecast_result = "Error: " . curl_error($ch);
        } else {
            $forecast_result = $response;
            $response_data = json_decode($response, true);

            if ($response_data['forecast_result'] === true) {
                // After the forecast result, check if the map image exists
                $map_file_name = "{$user_id}_{$weather_parameter}_forecast.gif";
                $map_image_path = "/var/www/html/user_maps/$map_file_name"; 

                if (file_exists($map_image_path)) {
                    $map_image_path = "https://skyskynthwaml.com/user_maps/$map_file_name"; // Update to the public URL
                } else {
                    $map_image_path = null; // Reset if file does not exist
                }
            }
        }

        curl_close($ch);
    }
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
            background-color: #282c34;
            color: #c0c0c0;
            text-align: center;
            padding: 0;
            margin: 0;
        }

        h1 {
            color: #61dafb;
        }

        .top-bar {
            background-color: #1e90ff;
            color: white;
            padding: 10px 0;
            text-align: center;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
            display: flex;
            justify-content: center;
        }

        .top-bar a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            font-size: 16px;
        }

        .top-bar a:hover {
            background-color: #61dafb;
            border-radius: 5px;
        }

        .content {
            margin-top: 60px;
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

        img {
            margin-top: 20px;
            max-width: 100%;
            border-radius: 10px;
        }
    </style>
</head>
<body>

<div class="top-bar">
    <a href="home_page.php">Home</a>
    <a href="settings.php">Account Settings</a>
    <a href="help.php">Resources</a>
    <a href="logout.php">Logout</a>
</div>

<div class="content">
    <div class="half-page">
        <h2>Request Forecast</h2>
        <form method="POST">
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

        <?php if (isset($forecast_result)): ?>
            <div>
                <h3>Forecast Result:</h3>
                <p><?php echo htmlspecialchars($forecast_result); ?></p>

                <?php if ($map_image_path): ?>
                    <h4>Generated Map:</h4>
                    <body>"<?php echo htmlspecialchars($map_image_path); ?>"</body>
                    <img src="<?php echo htmlspecialchars($map_image_path); ?>" alt="User Forecast Map">
                <?php endif; ?>
            </div>
        <?php endif; ?>
    </div>
    <div class="half-page">
        <h2>Request Geodetic Data</h2>
        <form method="POST">
            <input type="submit" name="request_geodetic" value="Request Geodetic Data" class="button">
        </form>
    </div>
</div>

</body>
</html>

