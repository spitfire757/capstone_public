<?php
session_start();
$servername = "localhost";
$username = "backend";
$password = "cobraSpitfire78!";
$dbname = "Capstone";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if (isset($_SESSION['User_ID']) && isset($_POST['latitude']) && isset($_POST['longitude'])) {
    $user_id = $_SESSION['User_ID'];
    $latitude = $_POST['latitude'];
    $longitude = $_POST['longitude'];

    // Check if the user already exists in the User_Lat table
    $check_sql_lat = "SELECT User_ID FROM User_Lat WHERE User_ID = ?";
    $stmt_check_lat = $conn->prepare($check_sql_lat);
    $stmt_check_lat->bind_param("i", $user_id);
    $stmt_check_lat->execute();
    $result_lat = $stmt_check_lat->get_result();

    if ($result_lat->num_rows > 0) {
        // User exists, update latitude
        $update_sql_lat = "UPDATE User_Lat SET Lat = ? WHERE User_ID = ?";
        $stmt_update_lat = $conn->prepare($update_sql_lat);
        $stmt_update_lat->bind_param("di", $latitude, $user_id);
        $stmt_update_lat->execute();
        $stmt_update_lat->close();
    } else {
        // User does not exist, insert latitude
        $insert_sql_lat = "INSERT INTO User_Lat (User_ID, Lat) VALUES (?, ?)";
        $stmt_insert_lat = $conn->prepare($insert_sql_lat);
        $stmt_insert_lat->bind_param("id", $user_id, $latitude);
        $stmt_insert_lat->execute();
        $stmt_insert_lat->close();
    }
    $stmt_check_lat->close();

    // Check if the user already exists in the User_Lon table
    $check_sql_lon = "SELECT User_ID FROM User_Lon WHERE User_ID = ?";
    $stmt_check_lon = $conn->prepare($check_sql_lon);
    $stmt_check_lon->bind_param("i", $user_id);
    $stmt_check_lon->execute();
    $result_lon = $stmt_check_lon->get_result();

    if ($result_lon->num_rows > 0) {
        // User exists, update longitude
        $update_sql_lon = "UPDATE User_Lon SET Lon = ? WHERE User_ID = ?";
        $stmt_update_lon = $conn->prepare($update_sql_lon);
        $stmt_update_lon->bind_param("di", $longitude, $user_id);
        $stmt_update_lon->execute();
        $stmt_update_lon->close();
    } else {
        // User does not exist, insert longitude
        $insert_sql_lon = "INSERT INTO User_Lon (User_ID, Lon) VALUES (?, ?)";
        $stmt_insert_lon = $conn->prepare($insert_sql_lon);
        $stmt_insert_lon->bind_param("id", $user_id, $longitude);
        $stmt_insert_lon->execute();
        $stmt_insert_lon->close();
    }
    $stmt_check_lon->close();

    echo "Location saved or updated successfully!";
} else {
    echo "User not signed in or missing data.";
}

$conn->close();
?>

