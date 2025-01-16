<?php
session_start();

// Database connection parameters
$servername = "localhost";
$username = "backend";
$password = "cobraSpitfire78!";
$dbname = "Capstone";

try {
    $db = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
    exit();
}

// Fetch user's latitude and longitude from the database
$user_id = $_SESSION['User_ID']; // Assuming the user is logged in

$query = $db->prepare("SELECT Lat, Lon FROM User_Lat JOIN User_Lon ON User_Lat.User_ID = User_Lon.User_ID WHERE User_Lat.User_ID = ?");
$query->execute([$user_id]);
$result = $query->fetch(PDO::FETCH_ASSOC);

if ($result) {
    $latitude = $result['Lat'];
    $longitude = $result['Lon'];

    // Call the Python script with latitude and longitude as arguments
    $command = escapeshellcmd("python3 /home/ubuntu/Capstone/analysis_onsite/weather_api.py $latitude $longitude");
    $output = shell_exec($command);

    // Output the result from the Python script
    echo "<pre>$output</pre>";
} else {
    echo "No latitude and longitude found for the user.";
}
?>

