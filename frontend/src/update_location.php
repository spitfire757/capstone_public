<?php
session_start();

// Database connection variables
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

// Check if user is signed in
if (!isset($_SESSION['Email'])) {
    echo "User is not signed in ----> REDIRECTING...";
    sleep(5);
    header("Location: index.php");
    exit();
}

$user_email = $_SESSION['Email'];

// Retrieve latitude and longitude from POST request
$latitude = $_POST['latitude'];
$longitude = $_POST['longitude'];

// Prepare and bind to get the user ID
$stmt = $conn->prepare("SELECT User_ID FROM User WHERE Email = ?");
$stmt->bind_param("s", $user_email);
$stmt->execute();
$stmt->bind_result($user_id);
$stmt->fetch();
$stmt->close();

if ($user_id) {
    // Update or insert latitude
    $stmt = $conn->prepare("INSERT INTO User_Lat (Lat, User_ID) VALUES (?, ?) ON DUPLICATE KEY UPDATE Lat = VALUES(Lat)");
    $stmt->bind_param("ii", $latitude, $user_id);
    
    if ($stmt->execute()) {
        // Update or insert longitude
        $stmt = $conn->prepare("INSERT INTO User_Lon (Lon, User_ID) VALUES (?, ?) ON DUPLICATE KEY UPDATE Lon = VALUES(Lon)");
        $stmt->bind_param("ii", $longitude, $user_id);
        
        if ($stmt->execute()) {
            echo "Location updated successfully!";
            header("Location: home_page.php");
        } else {
            echo "Error updating longitude: " . $stmt->error;
        }
        $stmt->close();
    } else {
        echo "Error updating latitude: " . $stmt->error;
    }
} else {
    echo "User not found...... REDIRECTING";
    sleep(5);
    header("Location: index.php");
    exit(); // Ensure no further code is executed after redirection
}

$conn->close();
?>
