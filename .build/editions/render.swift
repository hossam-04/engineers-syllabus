// Renders the print editions with the system's own WebKit, since this Mac has no HTML-to-PDF tool.
//   render pdf  IN.html OUT.pdf [IN.html OUT.pdf ...]   A4 pages, through the print system
//   render png  IN.html OUT.png WIDTH HEIGHT            a snapshot (the e-book covers)
//   render pages IN.pdf OUTDIR N [N ...]                page images, for checking the layout
//   render finish IN.pdf OUT.pdf TOC.json PAGES.json     find where each contents entry starts, then
//                                                        add bookmarks, page numbers and metadata
import Cocoa
import WebKit
import PDFKit

let args = Array(CommandLine.arguments.dropFirst())
guard let mode = args.first else { print("usage: render pdf|png|pages ..."); exit(2) }

if mode == "pages" {
    let doc = PDFDocument(url: URL(fileURLWithPath: args[1]))!
    for n in args.dropFirst(3).compactMap({ Int($0) }) {
        guard let page = doc.page(at: n - 1) else { continue }
        let box = page.bounds(for: .mediaBox)
        let img = page.thumbnail(of: NSSize(width: box.width * 1.4, height: box.height * 1.4), for: .mediaBox)
        let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
        try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: "\(args[2])/page-\(n).png"))
    }
    print("\(doc.pageCount) pages")
    exit(0)
}

// A page that draws its own number at the foot; PDFKit burns the drawing in when it saves.
final class NumberedPage: PDFPage {
    override func draw(with box: PDFDisplayBox, to context: CGContext) {
        super.draw(with: box, to: context)
        guard let doc = document else { return }
        let n = doc.index(for: self)
        if n == 0 { return }                                  // no number on the title page
        let bounds = self.bounds(for: box)
        let text = NSAttributedString(string: "\(n + 1)", attributes: [
            .font: NSFont(name: "Menlo", size: 7.5) ?? NSFont.monospacedSystemFont(ofSize: 7.5, weight: .regular),
            .foregroundColor: NSColor(calibratedWhite: 0.45, alpha: 1)])
        let line = CTLineCreateWithAttributedString(text)
        let w = CTLineGetTypographicBounds(line, nil, nil, nil)
        context.saveGState()
        context.textPosition = CGPoint(x: bounds.midX - CGFloat(w) / 2, y: bounds.minY + 24)
        CTLineDraw(line, context)
        context.restoreGState()
    }
}
final class PageClass: NSObject, PDFDocumentDelegate {
    func classForPage() -> AnyClass { NumberedPage.self }
}

func norm(_ s: String) -> String {
    s.lowercased().replacingOccurrences(of: "\u{2019}", with: "'")
        .components(separatedBy: .whitespacesAndNewlines).filter { !$0.isEmpty }.joined(separator: " ")
}

if mode == "finish" {
    let delegate = PageClass()
    guard let src = PDFDocument(url: URL(fileURLWithPath: args[1])) else { print("cannot read \(args[1])"); exit(1) }
    src.delegate = delegate                                   // before any page is touched, so pages are NumberedPage
    let meta = try! JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: args[3]))) as! [String: Any]
    let entries = meta["entries"] as! [[String: String]]
    let texts = (0..<src.pageCount).map { norm(src.page(at: $0)?.string ?? "") }
    let labels = entries.map { norm($0["label"]!) }
    // The contents pages list every entry; skip them when looking for where entries start.
    func isContents(_ t: String) -> Bool { labels.filter { t.contains($0) }.count >= 3 }
    var pages: [Int] = [], at = 1
    for e in entries {
        let key = norm(e["find"]!)
        var found = -1, i = at
        while i < texts.count {
            if !isContents(texts[i]) && String(texts[i].prefix(700)).contains(key) { found = i; break }
            i += 1
        }
        if found >= 0 { at = found }
        pages.append(found >= 0 ? found + 1 : -1)
    }
    try! JSONSerialization.data(withJSONObject: pages).write(to: URL(fileURLWithPath: args[4]))
    // Bookmarks: parts hold their chapters.
    let root = PDFOutline(); var part: PDFOutline? = nil
    for (e, n) in zip(entries, pages) where n > 0 {
        let item = PDFOutline(); item.label = e["label"]
        let page = src.page(at: n - 1)!
        item.destination = PDFDestination(page: page, at: CGPoint(x: 0, y: page.bounds(for: .mediaBox).maxY))
        if e["kind"] == "part" { root.insertChild(item, at: root.numberOfChildren); part = item }
        else if e["kind"] == "chapter", let p = part { p.insertChild(item, at: p.numberOfChildren) }
        else { root.insertChild(item, at: root.numberOfChildren); part = nil }
    }
    src.outlineRoot = root
    var attrs = src.documentAttributes ?? [:]
    attrs[PDFDocumentAttribute.titleAttribute] = meta["title"] as! String
    attrs[PDFDocumentAttribute.authorAttribute] = "The Engineer's Syllabus"
    attrs[PDFDocumentAttribute.creatorAttribute] = "The Engineer's Syllabus print edition"
    src.documentAttributes = attrs
    if !src.write(to: URL(fileURLWithPath: args[2])) { print("write failed"); exit(1) }
    print("pages \(src.pageCount), entries found \(pages.filter { $0 > 0 }.count)/\(pages.count)")
    exit(0)
}

final class Renderer: NSObject, WKNavigationDelegate {
    var jobs: [(URL, URL)]
    let web: WKWebView
    let window: NSWindow
    let size: NSSize
    let snapshot: Bool

    init(jobs: [(URL, URL)], size: NSSize, snapshot: Bool) {
        self.jobs = jobs; self.size = size; self.snapshot = snapshot
        web = WKWebView(frame: NSRect(origin: .zero, size: size))
        window = NSWindow(contentRect: NSRect(origin: .zero, size: size), styleMask: [.borderless], backing: .buffered, defer: false)
        super.init()
        window.contentView = web
        web.navigationDelegate = self
    }

    func next() {
        guard let (src, _) = jobs.first else { NSApp.terminate(nil); return }
        web.loadFileURL(src, allowingReadAccessTo: src.deletingLastPathComponent().deletingLastPathComponent())
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        // Wait for web fonts and the code highlighter before laying out pages.
        webView.evaluateJavaScript("document.fonts.ready.then(() => true)") { _, _ in
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) { self.render() }
        }
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) { fail(error) }
    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) { fail(error) }
    func fail(_ error: Error) { print("failed: \(jobs.first!.0.lastPathComponent): \(error)"); jobs.removeFirst(); next() }

    func render() {
        let (src, out) = jobs.first!
        if snapshot {
            let cfg = WKSnapshotConfiguration()
            cfg.rect = NSRect(origin: .zero, size: size)
            cfg.snapshotWidth = NSNumber(value: Double(size.width))   // points; the screen doubles it
            web.takeSnapshot(with: cfg) { img, _ in
                let rep = NSBitmapImageRep(data: img!.tiffRepresentation!)!
                try! rep.representation(using: .png, properties: [:])!.write(to: out)
                print("ok \(out.lastPathComponent)"); self.jobs.removeFirst(); self.next()
            }
            return
        }
        let info = NSPrintInfo()
        info.paperSize = NSSize(width: 595.28, height: 841.89)            // A4, in points
        info.topMargin = 46; info.bottomMargin = 50; info.leftMargin = 50; info.rightMargin = 50
        info.horizontalPagination = .fit
        info.verticalPagination = .automatic
        info.isHorizontallyCentered = false; info.isVerticallyCentered = false
        info.jobDisposition = .save
        info.dictionary()[NSPrintInfo.AttributeKey.jobSavingURL] = out
        let op = web.printOperation(with: info)
        op.showsPrintPanel = false; op.showsProgressPanel = false
        op.view?.frame = web.bounds
        op.runModal(for: window, delegate: self, didRun: #selector(printed(_:success:contextInfo:)), contextInfo: nil)
        _ = src
    }

    @objc func printed(_ op: NSPrintOperation, success: Bool, contextInfo: UnsafeMutableRawPointer?) {
        print((success ? "ok " : "FAILED ") + jobs.first!.1.lastPathComponent)
        jobs.removeFirst(); next()
    }
}

var jobs: [(URL, URL)] = []
var size = NSSize(width: 820, height: 1200)
if mode == "png" {
    jobs = [(URL(fileURLWithPath: args[1]), URL(fileURLWithPath: args[2]))]
    size = NSSize(width: Double(args[3])!, height: Double(args[4])!)
} else {
    var i = 1
    while i + 1 < args.count { jobs.append((URL(fileURLWithPath: args[i]), URL(fileURLWithPath: args[i + 1]))); i += 2 }
}
let app = NSApplication.shared
app.setActivationPolicy(.prohibited)
let renderer = Renderer(jobs: jobs, size: size, snapshot: mode == "png")
DispatchQueue.main.async { renderer.next() }
app.run()
