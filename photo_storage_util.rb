# Returns a list of valid storage options for photos
def get_list_of_storage_options()
    # Get list of external hard drives currently connected to the jetson
    usb_drives = %x`ls /media/$USER`
    list_usb_drives = usb_drives.split("\n")

    list_usb_drives.append("Default")
    return list_usb_drives
end

# Returns the path to which the photos will be saved depending on
# the user's device selection.
def get_photo_directory_path(selection="Default")
    user = %x`echo $USER`.delete("\n")
    photos_directory = '/HyperRailPhotos'

    if selection == "Default"
        # Default location for photos if external drive not connected
        dir_path = '/home/' + user + photos_directory

        if (!Dir.exist?(dir_path))
            %x`mkdir ~#{photos_directory}`
            puts("Created directory")
        end
        # Assign path variable to PHOTO_STORAGE_DIR const variable here

        return dir_path
    else
        # Maybe we should create an environment variable or global constant called PHOTO_STORAGE_DIR
        # and assign it this path. That way, the ROS node dedicated to capturing images will know
        # where to save them.
        path = '/media/' + user.delete("\n") + "/" + selection + photos_directory
        return path
    end
end