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

// Get the user's IP address
$ip = $_SERVER['REMOTE_ADDR'];

// Use an IP geolocation API to get the location (You can use ipinfo, ipapi, etc.)
$ip_info_url = "https://ipinfo.io/{$ip}/geo";
$location_data = file_get_contents($ip_info_url);
$location = json_decode($location_data);

if ($location && isset($location->loc)) {
    // Extract latitude and longitude from the response
    $lat_lon = explode(",", $location->loc);
    $latitude = floatval($lat_lon[0]);
    $longitude = floatval($lat_lon[1]);

    // Update the user's Lat and Lon in the database
    $user_id = $_SESSION['User_ID']; // Assuming the user is logged in

    // Update the Lat and Lon in User_Lat and User_Lon tables
    $update_lat_query = $db->prepare("UPDATE User_Lat SET Lat = ? WHERE User_ID = ?");
    $update_lat_query->execute([$latitude, $user_id]);

    $update_lon_query = $db->prepare("UPDATE User_Lon SET Lon = ? WHERE User_ID = ?");
    $update_lon_query->execute([$longitude, $user_id]);

    echo "Location updated for IP: $ip. Latitude: $latitude, Longitude: $longitude";
} else {
    echo "Unable to determine IP-based location.";
}
?>

