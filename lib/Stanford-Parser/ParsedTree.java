import java.util.Collection;
import java.util.List;
import java.io.StringReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.charset.Charset;
import java.nio.file.*;
import java.io.BufferedWriter;
import java.util.Set;
import java.util.HashSet;
import java.nio.file.StandardOpenOption;
import java.lang.StringBuilder;
import java.util.Collections;

import edu.stanford.nlp.process.TokenizerFactory;
import edu.stanford.nlp.process.CoreLabelTokenFactory;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import java.lang.reflect.*;
import edu.stanford.nlp.semgraph.*;
import edu.stanford.nlp.ling.IndexedWord;
import edu.stanford.nlp.util.Generics;
//import edu.stanford.nlp.trees.TypedDependency;

class ParsedTree {

  /**
   * The main method demonstrates the easiest way to load a parser.
   * Simply call loadModel and specify the path, which can either be a
   * file or any resource in the classpath.  For example, this
   * demonstrates loading from the models jar file, which you need to
   * include in the classpath for ParserDemo to work.
   */
  public static void main(String[] args) {
    LexicalizedParser lp = LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz");
    if (args.length > 0) {
      demoDP(lp, args[0], args[1]);
    } else {
      System.out.println("You should have mentioned a file name containing sentences.");
    }
  }

  /**
   * demoDP demonstrates turning a file into tokens and then parse
   * trees.  Note that the trees are printed by calling pennPrint on
   * the Tree object.  It is also possible to pass a PrintWriter to
   * pennPrint if you want to capture the output.
   */
  public static void demoDP(LexicalizedParser lp, String filename, String outname) {
    // This option shows loading and sentence-segmenting and tokenizing
    // a file using DocumentPreprocessor.
    TreebankLanguagePack tlp = new PennTreebankLanguagePack();
    GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
    // You could also create a tokenizer here (as below) and pass it
    // to DocumentPreprocessor
    for (List<HasWord> sentence : new DocumentPreprocessor(filename)) {
      // parse the sentece into a tree
      Tree parse = lp.apply(sentence);
      // create dependency structure
      GrammaticalStructure gs = gsf.newGrammaticalStructure(parse);
      Collection<TypedDependency> tdl = gs.typedDependenciesCCprocessed();
      //writeToFile(outname, tdl);
      SemanticGraph graph = new SemanticGraph(tdl);
      System.out.print(toString(graph));
      //System.out.println(graph);
      /*for (TypedDependency o : tdl){
          System.out.print(o);
          System.out.print('\t');
          try {
            Method treegraph = o.dep().getClass().getDeclaredMethod("treeGraph");
            treegraph.setAccessible(true);
            System.out.println(treegraph.invoke(o.dep()));
            //System.out.print('\t');
            //System.out.println(o.gov());
          } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
             System.out.println("Something Wroing in Reflection ");
             System.out.println(e);
          }
      }
      System.out.println();*/
    }
  }

  public static String toString(SemanticGraph graph) {
    Collection<IndexedWord> rootNodes = graph.getRoots();
    if (rootNodes.isEmpty()) {
      // Shouldn't happen, but return something!
      return("No Tree Found");
    }

    StringBuilder sb = new StringBuilder();
    Set<IndexedWord> used = Generics.newHashSet();
    for (IndexedWord root : rootNodes) {
      sb.append("(").append(root).append(" (root) \n");
      recToString(graph, root, sb, 1, used);
    }
    Set<IndexedWord> nodes = Generics.newHashSet(graph.vertexSet());
    nodes.removeAll(used);
    while (!nodes.isEmpty()) {
      IndexedWord node = nodes.iterator().next();
      sb.append(node);
      recToString(graph, node, sb, 1, used);
      nodes.removeAll(used);
    }
    sb.append(") \n");
    return sb.toString();
  }

  // helper for toString()
  private static void recToString(SemanticGraph graph, IndexedWord curr, StringBuilder sb, int offset, Set<IndexedWord> used) {
    used.add(curr);
    List<SemanticGraphEdge> edges = graph.outgoingEdgeList(curr);
    Collections.sort(edges);
    for (SemanticGraphEdge edge : edges) {
      IndexedWord target = edge.getTarget();
      sb.append(space(2*offset)).append("( ").append(target).append(" (").append(edge.getRelation()).append(") \n");
      if (!used.contains(target)) { // recurse
        recToString(graph, target, sb, offset + 1, used);
      }
      sb.append(space(2*offset)).append(") \n");
    }
  }

  private static String space(int width) {
    StringBuilder b = new StringBuilder();
    for (int i = 0; i < width; i++) {
      b.append(' ');
    }
    return b.toString();
  }


  public static void writeToFile(String filename, Collection<TypedDependency> tdl) {
    Path basepath = Paths.get("/home/ankur/devbench/scientific/support/dependency-parser/stanford-parser-full-2013-11-12");
    Path filepath = basepath.resolve(filename).normalize();
    Charset charset = Charset.forName("UTF-8");
    Set<OpenOption> options = new HashSet<OpenOption>();
    options.add(StandardOpenOption.CREATE);
    options.add(StandardOpenOption.WRITE);
    options.add(StandardOpenOption.TRUNCATE_EXISTING);
    try {
      BufferedWriter writer = Files.newBufferedWriter(filepath, charset, options.toArray(new OpenOption[0]));
      for (Object o : tdl) {
          writer.write(o.toString(), 0, o.toString().length());
      }
      System.out.println();
      writer.close();
    } catch (IOException e) {
        System.out.println("Problem openning the file");
        System.out.println(e);
    }
  }

  private ParsedTree() {} // static methods only

}
