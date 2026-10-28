    <div class="part" id="part2">
      <span class="part-num">Part II</span>
      <h2>The machine</h2>
      <p>Four chapters on what lies under the shell. Files and the names that point at them; who may read, change and run each one; the processes that run programs, and the environment each one inherits, including the <code>PATH</code> that decides which program a name means. The part ends with dotfiles, the small text files that configure your tools, kept in a repository with a script that installs them, which is the first half of the deliverable.</p>
    </div>

    <section class="chapter prose" id="ch05" data-ch="05">
      <header class="ch-head">
        <div class="ch-top"><span class="ch-num">Chapter 5</span><label class="done-toggle"><input type="checkbox" data-id="ch05"><span class="box"></span>Read</label></div>
        <h3>Files, paths and links</h3>
        <div class="ch-meta"><span>{{RT}} min read</span><span>{{EX}} exercises</span></div>
        <p class="thesis">A filesystem is a tree of names, and each name points to an <b>inode</b>, the record that holds a file's data, size, owner and permissions, but not its name. A path is directions through the tree. A <b>hard link</b> is a second name for the same inode, and a <b>symbolic link</b> is a small file that holds a path. Keeping those apart explains several everyday puzzles: why renaming a huge file is instant, why a symbolic link can break when nothing it points to was touched, and why deleting a log file doesn't always free the space.</p>
      </header>

      <h4>One tree, and directions through it</h4>
      <p>On Linux and macOS every file is somewhere in a single tree whose root is <code>/</code>. Other disks don't get letters as on Windows; they're <b>mounted</b> into the tree at a folder, such as <code>/Volumes/Backup</code> on a Mac or <code>/mnt/data</code> on Linux. A path that starts with <code>/</code> is <b>absolute</b>: directions from the root. Any other path is <b>relative</b>: directions from the current working directory, which <code>pwd</code> prints and <code>cd</code> changes. Every folder contains two special entries: <code>.</code>, the folder itself, and <code>..</code>, its parent. Section 1 of the example resolves a few paths the way the system does: <code>../data/./in.csv</code> from <code>/home/learner/project</code> is <code>/home/learner/data/in.csv</code>. <code>cd -</code> returns to the previous folder, and <code>~</code> is your home folder.</p>
      <p>Names starting with a dot are hidden from <code>ls</code> and from <code>*</code>, which is all "hidden" means. Linux treats <code>README.md</code> and <code>readme.md</code> as different names. A Mac's disk, by default, does not: it remembers the case you typed, but finds the file whatever case you ask for. So a Git repository containing both names, which is fine on Linux, breaks on a Mac, where only one of them can exist.</p>

      <h4>Names and inodes</h4>
      <p>A folder is a table that maps names to inode numbers, and the inode holds everything else about the file. <code>ls -i</code> shows the numbers, and <code>stat</code> shows the rest. Because the name isn't part of the file, renaming a file within one filesystem only rewrites an entry in a folder's table, which is why <code>mv</code> renames a ten-gigabyte video instantly. Moving it to another disk copies all the data and then deletes the original, because inode numbers only mean something within one filesystem. The rename is also <b>atomic</b>: anyone looking sees either the old name or the new one, never something in between. That's why "write a new file, then rename it over the old one" is the safe way to replace a file, as chapter 2 used.</p>

      <h4>Hard links and symbolic links</h4>
      <p><code>ln existing newname</code> makes a <b>hard link</b>: another entry, in the same or another folder, pointing at the same inode. Both names are equally real; neither is the original. The inode keeps a <b>link count</b>, the number of names pointing at it, and the file's data is freed only when that reaches zero. Hard links can't cross filesystems, and you can't make them to folders.</p>
      <p><code>ln -s target linkname</code> makes a <b>symbolic link</b>, or symlink: a tiny file whose contents are a path. Whenever something opens the link, the system reads that path and follows it, so a symlink can point at a folder, at another disk, or at nothing at all, in which case it's <b>broken</b>, or dangling. <code>ls -l</code> shows a symlink as <code>name -&gt; target</code>, and <code>readlink</code> prints the stored path. A relative target is resolved from the folder the <i>link</i> is in, not from wherever you were when you made it, which is the most common way dotfile links go wrong.</p>
      <figure class="diagram">
        <svg viewBox="0 0 760 290" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="On the left, a folder's table of names. notes.txt and hard.txt both point to inode A, which records a link count of 2, the owner and permissions, and the location of the data, version 2. soft.txt points to inode B, a symbolic link whose data is the path notes.txt, which is looked up again by name every time the link is used. On the right, after mv notes.txt renamed.txt: the table now holds renamed.txt and hard.txt, still pointing to inode A, unchanged, while soft.txt still holds the path notes.txt, which no longer names anything, so it is broken.">
          __SVG:fig05__
        </svg>
        <figcaption>Names point to inodes; a symbolic link points to a name. Renaming touches only the table, so a hard link never notices, and a symbolic link that relied on the old name breaks.</figcaption>
      </figure>
      <p>The example makes the commands' effects visible. It runs each command in bash, then inspects the results with Python's <code>os</code> module, labelling inodes A, B and so on, because the real numbers differ on every machine.</p>
      __EXAMPLE:ch05_files|files.py &middot; paths resolved, hard and symbolic links made, written through, renamed and deleted, a relative link resolved, and a deleted file still open__

      <h4>What the example shows</h4>
      <p><b>A hard link is the same file.</b> After <code>ln notes.txt hard.txt</code>, both names showed inode A and two names; writing <code>version 2</code> through <code>hard.txt</code> changed what <code>notes.txt</code> contains, because there's only one file. Renaming <code>notes.txt</code> left inode A and its contents exactly as they were. Deleting <code>renamed.txt</code> dropped the count to one name, and <code>hard.txt</code> still holds the data. The symlink went the other way. It held the path <code>notes.txt</code> all along, so the moment that name stopped existing, the link broke, though nothing it once reached had been deleted at the time.</p>
      <p><b>A relative link is read from where it lives.</b> In section 4, both links were made from the same folder, but stored different text. <code>home/.zshrc</code> holds <code>dotfiles/zshrc</code>, which, read from inside <code>home</code>, means <code>home/dotfiles/zshrc</code>, which doesn't exist. <code>../dotfiles/zshrc</code> climbs out of <code>home</code> first, and works. And section 5 showed the reason a full disk can survive a cleanup. After <code>rm big.log</code> the name was gone, but the program that had the file open could still use all million bytes, and the inode had zero names. The space returns only when that program closes the file or exits.</p>

      <h4>Where things live</h4>
      <p>The layout of the tree is conventional, and knowing it saves searching. Programs live in <code>/usr/bin</code> and <code>/bin</code>, and ones you install yourself in <code>/usr/local/bin</code>; on Apple silicon Macs, Homebrew uses <code>/opt/homebrew</code>. System configuration lives in <code>/etc</code>, logs in <code>/var/log</code>, temporary files in <code>/tmp</code>. Your own files and settings are under your home folder, <code>/Users/you</code> on a Mac and <code>/home/you</code> on Linux, and many programs keep their settings in <code>~/.config</code>, which chapter 8 uses. <code>df -h</code> shows how full each mounted filesystem is, and <code>du -sh folder</code> how much a folder uses; when they disagree, a deleted file that's still open is the usual reason.</p>

      <div class="traps">
        <h5 class="block-h">Common traps</h5>
        <ul>
          <li><b>A relative symlink</b> whose target was written relative to the wrong folder.</li>
          <li><b>Deleting a big log file</b> that a running program still has open, and expecting the space back.</li>
          <li><b>Two names that differ only in case,</b> which are one file on a Mac.</li>
          <li><b>Assuming <code>mv</code> is instant and safe everywhere:</b> across disks it copies, and can be interrupted halfway.</li>
          <li><b>Editing a file through a hard link</b> and forgetting the other name changes too.</li>
        </ul>
      </div>

      <div class="exercises">
        <h5 class="block-h">Exercises</h5>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 5.1</span><span class="ex-title">Which names share a file?</span></div>
          <p>After <code>echo a &gt; f; ln f g; ln -s f s; cp f c; mv f f2</code>, which names exist, which share an inode, what is each one's link count, and does <code>s</code> work?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-plaintext">f     gone: renamed to f2
f2    inode A, 2 names
g     inode A, 2 names
s     symbolic link to "f", broken
c     inode B, 1 name: a copy is a new file</code></pre>
            <p><code>ln f g</code> gave inode A a second name. <code>cp</code> made a new inode with the same contents, so <code>c</code> is independent from then on. <code>mv f f2</code> renamed one of A's two names, leaving the count at two, and since <code>s</code> holds the text <code>f</code>, it broke. Running the commands confirms all five lines. Note that changing <code>f2</code> or <code>g</code> changes both, while changing <code>c</code> changes only <code>c</code>. That difference matters for backups: a "backup" made by hard-linking your files isn't one, because editing the original edits the backup too.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 5.2</span><span class="ex-title">The disk that stayed full</span></div>
          <p>A server's disk is at 100%. You delete a 40-gigabyte log file, and <code>df</code> still says 100%, while <code>du</code> finds only 2 gigabytes in use. What's going on, and how do you fix it?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <pre><code class="language-bash">sudo lsof +L1                 # open files with a link count below 1: deleted, but still open
: > /proc/1234/fd/7           # Linux: empty the deleted file through the process holding it
sudo systemctl restart myapp  # or restart the program, which closes it</code></pre>
            <p><code>du</code> adds up the files it can find by name, and <code>df</code> asks the filesystem how many blocks are in use. The difference is a file with no name that's still in use: the program writing the log still has it open, so <code>rm</code> removed the name, but the inode and its 40 gigabytes stay until the program closes it. <code>lsof +L1</code> lists exactly such files, with the process and its file descriptor. Restarting the program frees the space; on Linux you can also empty the file through <code>/proc</code>, without a restart. The lesson for next time: to shrink a log a program is writing, truncate it with <code>: &gt; app.log</code> instead of deleting it, or better, configure log rotation, which renames the file and tells the program to reopen it.</p>
          </div></details>
        </div>

        <div class="exercise">
          <div class="ex-head"><span class="ex-num">Exercise 5.3</span><span class="ex-title">The dotfile link</span></div>
          <p>Your settings are in <code>~/dotfiles/zshrc</code>. Which of these make a working <code>~/.zshrc</code>: (a) <code>cd ~/dotfiles &amp;&amp; ln -s zshrc ~/.zshrc</code>, (b) <code>cd ~ &amp;&amp; ln -s dotfiles/zshrc .zshrc</code>, (c) <code>cd /tmp &amp;&amp; ln -s dotfiles/zshrc ~/.zshrc</code>, (d) <code>cd ~/dotfiles &amp;&amp; ln -s "$PWD/zshrc" ~/.zshrc</code>?</p>
          <details class="solution"><summary>Show solution</summary><div class="sol-body">
            <p>(a) is broken; (b), (c) and (d) work. Only the stored text matters, read from the link's folder, <code>~</code>. In (a) the link holds <code>zshrc</code>, so it points at <code>~/zshrc</code>, which doesn't exist. Being in <code>~/dotfiles</code> when you typed the command made no difference. (b) and (c) store <code>dotfiles/zshrc</code>, which from <code>~</code> means <code>~/dotfiles/zshrc</code>, whichever folder you were in. (d) stores an absolute path, which works from anywhere but breaks if you move the repository, while a relative link keeps working as long as the link and its target move together. Making all four confirms it. Install scripts, like chapter 8's, usually store absolute paths and recreate the links if the repository moves.</p>
          </div></details>
        </div>
      </div>

      <div class="ch-end">
        <div>
          <h5 class="block-h">Checklist</h5>
          <ul class="checklist">
            <li>Can you resolve any relative path to an absolute one in your head?</li>
            <li>Can you explain what an inode holds, and why renaming is instant and atomic?</li>
            <li>Can you say how hard links and symbolic links differ, and when each breaks?</li>
            <li>Can you write a relative symlink that points where you mean?</li>
            <li>Can you find a deleted file that's still holding disk space?</li>
          </ul>
        </div>
        <div>
          <h5 class="block-h">Go deeper</h5>
          <ul class="res">
            <li><span class="rkind free">Book</span><div><a href="https://linuxcommand.org/tlcl.php">The Linux Command Line</a> <span class="by">William Shotts</span></div></li>
            <li><span class="rkind free">Book</span><div><a href="https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf">Operating Systems: Three Easy Pieces, Files and Directories</a> <span class="by">Arpaci-Dusseau &amp; Arpaci-Dusseau</span></div></li>
            <li><span class="rkind free">Docs</span><div><a href="https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html">Filesystem Hierarchy Standard</a> <span class="by">The Linux Foundation</span></div></li>
          </ul>
        </div>
      </div>
    </section>
