---

# movian-repo  
A script to generate the Movian plugin repository JSON file

## How to Publish Plugins

Starting with Movian 6.0, multiple plugin feeds are supported. For more information on how to add new feeds to Movian, see this article.

**Note**: There is no longer a central plugin repository hosted on this site. See [this article](https://www.movian.tv/articles/) for more information.

The easiest way to publish plugins is to commit each plugin to a public GitHub repository.

For an example of how this should look, check out the [movian-plugin-modarchive](https://github.com/andoma/movian-plugin-modarchive) repository.

Then you can use the `movian-repo` tool found [here](https://github.com/czz/movian-repo) to generate the plugin feed.

Currently, this tool only works with plugins hosted on GitHub or other accessible links.

### How to Use

1. **Create a `repos.txt` file** and fill it with GitHub repository names or direct links to ZIP archives of plugins. For example:
   ```
   /andoma/movian-plugin-sidplayer
   /andoma/movian-plugin-xmpplayer
   /andoma/movian-plugin-gmeplayer
   https://drive.google.com/uc?id=1OCplxxxxxxxxxxxxxxAajdMHAAL
   https://github.com/andoma/movian-plugin-modarchive/archive/refs/heads/main.zip
   ```

2. **Run the script** `build.py` with the following parameters:
   ```
   python build.py -i repos.txt -o repo.json
   ```

3. After the script finishes, it will generate a `repo.json` file containing information about the plugins, including download links for the archives and icons (for ZIP archives and Google Drive links).

4. You can upload this file to GitHub Pages or host it however you like. Then, share the URL with your users.

### Command-Line Arguments:

- `-i` or `--inputfile`: The file containing a list of GitHub repository names or direct links to ZIP archives. The default input file is `repos.txt`.
- `-o` or `--outputfile`: The name of the output file where the JSON will be saved. The default output file is `repo.json`.
- `-t` or `--title`: A title for the plugin feed (optional).

### Example

1. **Example `repos.txt`**:
   ```
   /andoma/movian-plugin-sidplayer
   https://github.com/andoma/movian-plugin-xmpplayer/archive/refs/heads/main.zip
   https://drive.google.com/uc?id=1OCplxxxxxxxxxxajdMHAAL
   ```

2. **Run the script**:
   ```
   python build.py -i repos.txt -o repo.json -t "Movian Plugin Feed"
   ```

3. **Generated `repo.json`**:
   ```json
   {
     "version": 1,
     "title": "Movian Plugin Feed",
     "plugins": [
       {
         "type": "ecmascript",
         "id": "modarchive",
         "file": "modarchive.js",
         "icon": "https://raw.githubusercontent.com/andoma/movian-plugin-modarchive/98a418ea13a338ee3167e87ea5e5c699efe1ca8e/logo.png",
         "category": "music",
         "showtimeVersion": "4.8",
         "version": "2.1",
         "author": "Andreas Smas",
         "title": "The Mod Archive",
         "synopsis": "Welcome to one of the world's largest collections of music modules",
         "description": "Enjoy music from the past",
         "downloadURL": "https://github.com/andoma/movian-plugin-modarchive/archive/98a418ea13a338ee3167e87ea5e5c699efe1ca8e.zip"
       },
       {
         "type": "ecmascript",
           .
           .
           .
         "description": "<p>anilibria plugin - is the integration of the website <a href=\"https://www.anilibria.tv\">www.anilibria.tv</a> into Movian",
         "downloadURL": "https://drive.google.com/uc?id=1OCplMxxxxxxxxxxxxxxMHAAL"
       }
     ]
   }
   ```

### How It Works

1. **For GitHub Repositories**:
   - The script extracts the `plugin.json` file from the repository and adds the plugin data to the JSON, including the download link for the plugin archive and the icon.
   - For each repository, a download link is generated using the GitHub URL and the commit SHA.

2. **For Direct ZIP File Links**:
   - The script downloads the ZIP archive, extracts the `plugin.json` file and the icon.
   - If an icon is found in the archive, it is saved to the local `icons` folder with a name based on the plugin's `id`.
   - The final JSON includes the path to the local icon.

3. **For Google Drive Links**:
   - The script converts Google Drive links into direct download links, then processes them as ZIP archives by downloading and extracting the plugin and icon.

### Output File Structure (`repo.json`)

The output JSON file contains the plugin data with the following fields:

- `type`: The type of plugin (e.g., `ecmascript`).
- `id`: The unique identifier for the plugin.
- `file`: The entry file of the plugin.
- `icon`: The URL or path to the plugin's icon.
- `category`: The category of the plugin (e.g., `music`, `video`).
- `showtimeVersion`: The minimum Showtime version required.
- `version`: The plugin version.
- `author`: The author of the plugin.
- `title`: The title of the plugin.
- `synopsis`: A short description or link to a website for the plugin.
- `description`: A detailed description of the plugin.
- `downloadURL`: The URL for downloading the plugin archive.

---
