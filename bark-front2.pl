#!/usr/bin/perl
use strict;
use warnings;
use CGI ":standard";
use HTTP::Async;
use HTTP::Request;
use JSON;
use POSIX qw(log10);
use Fcntl qw(:flock);

print header("text/html");

my $datestring = localtime();
my $file_path = '/var/www/html/bark.txt';

# Create an HTTP::Async object
my $async = HTTP::Async->new;

# Make the HTTP request
my $url = 'http://192.168.1.48:8090/q.json?cmd=queryLevel&ot=1&oid=6';
my $request = HTTP::Request->new(GET => $url);
$async->add($request);

# Process the asynchronous requests
while (my $response = $async->wait_for_next_response) {
    if ($response->is_success) {
        # Decode the JSON response
        my $json = decode_json($response->decoded_content);

        # Extract values from the JSON and save as variables
        my $result = $json->{result};
        my $level = $json->{level};

        # Calculate sound decibel (dB) from level
        my $dB = 40 * log10($level);

        my $output = "F |Bark Detected | $datestring | Level: $level | dB: $dB\n";

        print "S JSON: $json\n";
        print "Level: $level\n";
        print "dB: $dB\n";

        # Check if the new line is a duplicate
        my $is_duplicate = 0;
        if (-e $file_path) {
            open(my $read_handle, '<', $file_path) or die "Can't open file: $file_path - $!";
            flock($read_handle, LOCK_SH);
            while (my $line = <$read_handle>) {
                chomp($line);
                if ($line eq $output) {
                    $is_duplicate = 1;
                    last;
                }
            }
            flock($read_handle, LOCK_UN);
            close($read_handle);
        }

        # Write the extracted values to the file if it's not a duplicate
        if (!$is_duplicate) {
            open(my $file_handle, '>>', $file_path) or die "Can't open file: $file_path - $!";
            flock($file_handle, LOCK_EX);
            print $file_handle $output;
            flock($file_handle, LOCK_UN);
            close($file_handle);
        }
    } else {
        # If the request failed, write an error message to the file
        my $error_message = "Bark Detected | $datestring\n";
        $error_message .= "Error fetching JSON: " . $response->status_line . "\n";

        open(my $file_handle, '>>', $file_path) or die "Can't open file: $file_path - $!";
        flock($file_handle, LOCK_EX);
        print $file_handle $error_message;
        flock($file_handle, LOCK_UN);
        close($file_handle);
    }
}

