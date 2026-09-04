## 1. Hello world

```cpp
#include <iostream>

int main() {
    std::cout << "Bonjour le monde !" << std::endl;
    return 0;
}
```

## 2. Entrées/sorties et variables

`std::cin` pour lire, `std::cout` pour écrire.

```cpp
std::string prenom;
int age;

std::cin >> prenom;
std::cin >> age;

std::cout << "Salut " << prenom << " ! Dans 10 ans tu auras " << age + 10 << " ans." << std::endl;
```

## 3. Conditions

```cpp
if (age < 0) {
    std::cout << "Ca n'existe pas un age negatif !" << std::endl;
} else if (age < 18) {
    std::cout << "Tu es mineur, il te reste " << 18 - age << " ans avant d'etre majeur." << std::endl;
} else if (age == 18) {
    std::cout << "Tout juste majeur !" << std::endl;
} else {
    std::cout << "Tu es majeur depuis " << age - 18 << " ans." << std::endl;
}
```

## 4. Boucles

`for` (nombre d'itérations connu) vs `while` (condition).

```cpp
for (int i = 1; i <= 5; i++) {
    std::cout << i << std::endl;
}

int n = 5;
while (n > 0) {
    std::cout << n << std::endl;
    n--;
}
```

## 5. Fonctions

Découpage d'un programme (jeu du nombre secret) en fonctions avec ou sans retour.

```cpp
// void : ne retourne rien
void afficherBienvenue() {
    std::cout << "=== Jeu du nombre secret ===" << std::endl;
}

// retourne un int
int genererSecret() {
    return rand() % 100 + 1;
}

// prend un paramètre, retourne un string
std::string evaluerScore(int essais) {
    if (essais <= 5) return "Impressionnant !";
    if (essais <= 10) return "Pas mal !";
    return "Continue de t'entrainer...";
}
```

Le jeu complet avec boucle `while (true)` + `break` reprend les mêmes fonctions dans un seul fichier.

## 6. Tableaux et vector

Tableau classique = taille fixe. `std::vector` = taille dynamique.

```cpp
int notes[5] = {14, 17, 9, 12, 18};

std::vector<int> scores;
scores.push_back(42);
scores.push_back(87);

// for moderne (range-based)
for (int score : scores) {
    std::cout << score << std::endl;
}

scores.pop_back(); // supprime le dernier élément
```

## 7. Structs

Regrouper des données liées dans un même type.

```cpp
struct Etudiant {
    std::string prenom;
    int age;
    std::vector<int> notes;
};

Etudiant alice;
alice.prenom = "Alice";
alice.age = 20;
alice.notes = {14, 16, 12, 18};
```

## 8. Fichiers

Écriture/lecture avec `ofstream` / `ifstream`.

```cpp
std::ofstream writer("test.txt");
writer << "Ligne 1 : bonjour" << std::endl;
writer.close();

std::ifstream reader("test.txt");
std::string ligne;
while (std::getline(reader, ligne)) {
    std::cout << "  > " << ligne << std::endl;
}

// ajouter sans écraser
std::ofstream appender("test.txt", std::ios::app);
```

## 9. Pointeurs

`&` = adresse d'une variable, `*` = valeur pointée.

```cpp
int age = 25;
int* ptr = &age;

std::cout << *ptr << std::endl; // valeur pointée : 25
*ptr = 30;                      // modifie age via le pointeur

void doubler(int* p) {
    *p = *p * 2;
}
doubler(&age);

// allocation dynamique
int* nombre = new int(42);
delete nombre; // toujours libérer après new
```

## 10. Classes

Encapsulation : données privées + méthodes publiques, constructeur.

```cpp
class Etudiant {
    std::string prenom;
    int age;
    std::vector<int> notes;

public:
    Etudiant(std::string p, int a) {
        prenom = p;
        age = a;
    }

    void ajouterNote(int note) {
        if (note < 0 || note > 20) return;
        notes.push_back(note);
    }

    double getMoyenne() {
        if (notes.empty()) return 0;
        int total = 0;
        for (int note : notes) total += note;
        return total / (double)notes.size();
    }
};
```

## 11. Héritage et polymorphisme

Une classe de base avec méthode `virtual`, des classes filles qui l'`override`.

```cpp
class Personne {
public:
    Personne(std::string p, int a) { prenom = p; age = a; }
    virtual void afficher() {
        std::cout << prenom << " (" << age << " ans)";
    }
    std::string prenom; int age;
};

class Etudiant : public Personne {
public:
    Etudiant(std::string p, int a) : Personne(p, a) {}

    void afficher() override {
        Personne::afficher();
        std::cout << " - etudiant - moyenne : " << getMoyenne() << std::endl;
    }
};

// polymorphisme : un pointeur de base peut désigner n'importe quelle classe fille
std::vector<Personne*> liste = {&alice, &bob};
for (Personne* p : liste) {
    p->afficher(); // appelle la bonne version selon le type réel
}
```

## 12. Smart pointers

Gestion automatique de la mémoire, plus de `delete` manuel.

```cpp
// unique_ptr : un seul propriétaire, détruit automatiquement en fin de bloc
std::unique_ptr<Robot> r2 = std::make_unique<Robot>("R2");
std::unique_ptr<Robot> r3 = std::move(r2); // transfert de propriété (pas de copie possible)

// shared_ptr : plusieurs propriétaires, compteur de références
std::shared_ptr<Robot> s1 = std::make_shared<Robot>("S1");
std::shared_ptr<Robot> s2 = s1; // copie OK, ils partagent l'objet
std::cout << s1.use_count() << std::endl; // 2
// l'objet n'est détruit que quand le dernier shared_ptr disparaît
```

## 13. Filesystem

Manipuler fichiers/dossiers avec `std::filesystem`.

```cpp
namespace fs = std::filesystem;

fs::path p = "C:/Users";
fs::exists(p);
fs::is_directory(p);

fs::create_directory("dossier_test");
fs::remove_all("dossier_test"); // supprime dossier + contenu

for (const fs::directory_entry& entry : fs::directory_iterator(".")) {
    std::cout << entry.path().filename().string() << std::endl;
}

// parcours récursif, filtré par extension
for (const fs::directory_entry& entry : fs::recursive_directory_iterator(".")) {
    if (entry.path().extension() == ".cpp") {
        std::cout << entry.path().string() << std::endl;
    }
}
```

## 14. Lancer des processus (Windows)

Trois niveaux, du plus simple au plus contrôlé.

```cpp
// Niveau 1 : system() — bloque, mais pas de lecture de la sortie
int code = system("echo Bonjour depuis system()");

// Niveau 2 : _popen() — lit la sortie de la commande via un pipe
FILE* pipe = _popen("dir /b", "r");
char buffer[256];
while (fgets(buffer, sizeof(buffer), pipe)) {
    std::cout << "  > " << buffer;
}
_pclose(pipe);

// Niveau 3 : CreateProcess() — API Windows, contrôle total (PID, arrêt forcé...)
STARTUPINFOA si = { sizeof(si) };
PROCESS_INFORMATION pi;
char commande[] = "mspaint.exe";

CreateProcessA(NULL, commande, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi);
Sleep(3000);
TerminateProcess(pi.hProcess, 0);
CloseHandle(pi.hProcess);
CloseHandle(pi.hThread);
```
