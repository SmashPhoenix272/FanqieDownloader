# Fanqie Novel Downloader

This tool allows you to download novels from Fanqie Novel using your own API ( get from Lsposed ). It includes an improved caching functionality to avoid re-downloading previously downloaded chapters and provides an enhanced command-line interface.

## Features

- Download novels from Fanqie Novel
- Improved caching system:
  - Separate tables for novel info and chapters in SQLite database
  - Individual files for chapter content caching
  - Metadata for better tracking and management
- Retry mechanism for handling invalid chapter content
- Progress bar for better download tracking
- Command-line interface for easy use

## Setup

1. Ensure you have Python 3.7+ installed on your system.
2. Install the required dependencies:
   ```
   pip install requests python-dotenv tqdm
   ```
3. Create a `.env` file in the project root and add the following line:
   ```
   FANQIE_API_URL=your_api_url_here
   ```

   Replace `your_api_url_here` with the actual URL of the Fanqie Novel API.

## Usage

Run the script with the following command:

```
python fanqie_downloader.py
```

You will be prompted to enter the novel ID you want to download. The script will then download the novel, showing a progress bar for the chapter downloads.

## Project Structure

- `fanqie_downloader.py`: Main script for downloading novels
- `cache.py`: Module for handling improved SQLite-based caching functionality
- `.env`: Configuration file for API URL
- `novel_cache/`: Directory containing the SQLite database and individual chapter cache files
- `claudeDev_docs/`: Documentation folder
  - `currentTask.md`: Current task overview
  - `projectRoadmap.md`: Project goals and milestones
  - `techStack.md`: Technology choices and architecture decisions
  - `codebaseSummary.md`: Project structure and key components

## Improved Caching System

The project now uses an enhanced SQLite-based caching system:

1. Separate tables for novel info and chapters in the SQLite database
2. Individual files for storing chapter content, improving performance for large novels
3. Metadata (last_updated timestamp) added to both novel info and chapter caches for better tracking and management

This new system provides better performance, data integrity, and management capabilities compared to the previous caching system.

## Retry Mechanism

The downloader includes a retry mechanism for handling invalid chapter content. It will attempt to download a chapter up to 3 times before moving on to the next chapter.

## Contributing

Feel free to submit issues or pull requests if you have any suggestions or improvements.

## License

This project is open-source and available under the MIT License.
